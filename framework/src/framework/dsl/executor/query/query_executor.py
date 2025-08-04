# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from functools import partial, reduce

import numpy as np
import structlog
from beartype.typing import Any, Sequence, cast

from superlinked.framework.common.dag.context import (
    CONTEXT_COMMON,
    CONTEXT_COMMON_NOW,
    ExecutionContext,
    ExecutionEnvironment,
    NowStrategy,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InvalidInputException,
    InvalidStateException,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.knn_search_params import (
    KNNSearchParams,
)
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.common.telemetry.telemetry_registry import telemetry
from superlinked.framework.dsl.executor.executor import App
from superlinked.framework.dsl.query.clause_params import (
    KNNSearchClauseParams,
    MetadataExtractionClauseParams,
    QueryVectorClauseParams,
)
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor
from superlinked.framework.dsl.query.query_param_value_setter import (
    QueryParamValueSetter,
)
from superlinked.framework.dsl.query.query_vector_factory import QueryVectorFactory
from superlinked.framework.dsl.query.result import (
    QueryResult,
    ResultEntry,
    ResultEntryMetadata,
    ResultMetadata,
)

logger = structlog.getLogger()


class QueryExecutor:
    """
    QueryExecutor provides an interface to execute predefined queries with query time parameters.
    """

    def __init__(
        self,
        app: App,
        query_descriptor: QueryDescriptor,
        query_vector_factory: QueryVectorFactory,
    ) -> None:
        """
        Initializes the QueryExecutor.

        Args:
            app: An instance of the App class.
            query_descriptor: An instance of the QueryDescriptor class representing the query to be executed.
            query_vector_factory: An instance of the QueryVectorFactory class used to produce query vectors.
        """
        self.app = app
        self._query_descriptor = query_descriptor
        self.query_vector_factory = query_vector_factory
        self._logger = logger.bind(schema=self._query_descriptor.schema._schema_name)

    async def query(self, **params: ParamInputType | None) -> QueryResult:
        """
        Execute a query with keyword parameters.

        Args:
            **params: Arbitrary arguments with keys corresponding to the `name` attribute of the `Param` instance.

        Returns:
            Result: The result of the query execution that can be inspected and post-processed.

        Raises:
            InvalidInputException: If the query index is not amongst the executor's indices.
        """
        self.__check_executor_has_index()
        query_descriptor: QueryDescriptor = await QueryParamValueSetter.set_values(self._query_descriptor, params)
        knn_search_params: KNNSearchParams = await self._produce_knn_search_params(query_descriptor)
        entities = await self._knn_search(
            knn_search_params,
            query_descriptor,
            knn_search_params.should_return_index_vector or query_descriptor.with_metadata,
        )
        self._logger.info(
            "executed query",
            n_results=len(entities),
            limit=knn_search_params.limit,
            radius=knn_search_params.radius,
            pii_knn_params=params,
            pii_query_vector=partial(str, knn_search_params.vector),
        )
        query_vector = knn_search_params.vector
        metadata = ResultMetadata(
            schema_name=query_descriptor.schema._schema_name,
            search_vector=query_vector.to_list(),
            search_params=self._map_search_params(query_descriptor),
        )
        entry_metadata = self._calculate_metadata_of_entries(
            query_descriptor.schema, entities, query_vector, query_descriptor
        )
        return QueryResult(entries=self._map_entities(entities, entry_metadata), metadata=metadata)

    def _calculate_metadata_of_entries(
        self,
        schema: IdSchemaObject,
        entities: Sequence[SearchResultItem],
        query_vector: Vector,
        query_descriptor: QueryDescriptor,
    ) -> list[ResultEntryMetadata]:
        metadata_extraction_params = reduce(
            lambda params, clause: clause.get_altered_metadata_extraction_params(params),
            query_descriptor.clauses,
            MetadataExtractionClauseParams(),
        )
        partial_scores = self._get_partial_scores(entities, query_vector, query_descriptor.with_metadata)
        all_vector_parts = self._get_vector_parts(schema, entities, metadata_extraction_params.vector_part_ids)
        return [
            ResultEntryMetadata(
                score=entity.score,
                partial_scores=partial_score,
                vector_parts=[vector_part.to_list() for vector_part in vector_parts],
            )
            for entity, partial_score, vector_parts in zip(entities, partial_scores, all_vector_parts)
        ]

    def _get_partial_scores(
        self, entities: Sequence[SearchResultItem], query_vector: Vector, with_partial_scores: bool
    ) -> list[list[float]]:
        if with_partial_scores:
            result_vectors = [
                entity.index_vector or Vector.init_zero_vector(query_vector.dimension) for entity in entities
            ]
            return self._calculate_partial_scores(query_vector, result_vectors)
        return [list[float]()] * len(entities)

    def _get_vector_parts(
        self, schema: IdSchemaObject, entities: Sequence[SearchResultItem], vector_part_ids: Sequence[str]
    ) -> list[list[Vector]]:
        def get_empty_result() -> list[list[Vector]]:
            return [list[Vector]()] * len(entities)

        if not vector_part_ids:
            return get_empty_result()
        context = self._create_query_context_base(context_time=None)
        vectors = self._get_vectors_for_vector_parts(entities)
        all_vector_parts = self.query_vector_factory.get_vector_parts(vectors, vector_part_ids, schema, context)
        return get_empty_result() if all_vector_parts is None else all_vector_parts

    def _get_vectors_for_vector_parts(self, entities: Sequence[SearchResultItem]) -> list[Vector]:
        index_vector_by_object_id = {entity.header.object_id: entity.index_vector for entity in entities}
        if unqueried_entity_ids := [
            object_id for object_id, vector in index_vector_by_object_id.items() if vector is None
        ]:
            raise InvalidStateException(
                "Vector parts can only be requested with queried index vector. "
                "Index vectors of entity ids cannot be found.",
                entity_ids=unqueried_entity_ids,
            )
        return cast(list[Vector], list(index_vector_by_object_id.values()))

    def _map_entities(
        self, entities: Sequence[SearchResultItem], entry_metadata: Sequence[ResultEntryMetadata]
    ) -> list[ResultEntry]:
        return [
            ResultEntry(
                id=entity.header.origin_id or entity.header.object_id,
                fields={field.schema_field.name: field.value for field in entity.fields},
                metadata=metadata,
            )
            for entity, metadata in zip(entities, entry_metadata)
        ]

    def _map_search_params(self, query_descriptor: QueryDescriptor) -> dict[str, Any]:
        return {
            item: value
            for clause in query_descriptor.clauses
            for item, value in clause.get_param_value_by_param_name().items()
        }

    async def _produce_knn_search_params(self, query_descriptor: QueryDescriptor) -> KNNSearchParams:
        query_vector = await self._produce_query_vector(query_descriptor)
        partial_knn_search_params = reduce(
            lambda params, clause: clause.get_altered_knn_search_params(params),
            query_descriptor.clauses,
            KNNSearchClauseParams(),
        )
        return KNNSearchParams.from_clause_params(query_vector, partial_knn_search_params)

    async def _produce_query_vector(self, query_descriptor: QueryDescriptor) -> Vector:
        query_vector_params = QueryVectorClauseParams()
        for clause in query_descriptor.clauses:
            query_vector_params = await clause.get_altered_query_vector_params(
                query_vector_params, query_descriptor.index._node_id, query_descriptor.schema, self.app.storage_manager
            )
        context = self._create_query_context_base(query_vector_params.context_time)
        return await self.query_vector_factory.produce_vector(
            query_vector_params.query_node_inputs_by_node_id,
            query_vector_params.weight_by_space,
            query_descriptor.schema,
            context,
        )

    def _create_query_context_base(self, context_time: int | None) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY,
            data=self.app._context.data,
            now_strategy=NowStrategy.CONTEXT_TIME,
        )
        context_time = context_time if context_time is not None else self.app._context.now()
        eval_context.update_data({CONTEXT_COMMON: {CONTEXT_COMMON_NOW: context_time}})
        return eval_context

    async def _knn_search(
        self,
        knn_search_params: KNNSearchParams,
        query_descriptor: QueryDescriptor,
        should_return_index_vector: bool,
    ) -> Sequence[SearchResultItem]:
        with telemetry.span(
            "storage.knn",
            attributes={
                "index": query_descriptor.index._node_id,
                "schema": query_descriptor.schema._schema_name,
                "n_clauses": len(query_descriptor.clauses),
                "limit": knn_search_params.limit,
                "radius": knn_search_params.radius,
                "should_return_index_vector": should_return_index_vector,
            },
        ):
            return await self.app.storage_manager.knn_search(
                query_descriptor.index._node,
                query_descriptor.schema,
                knn_search_params,
                query_descriptor.query_user_config,
                should_return_index_vector,
            )

    def _calculate_partial_scores(self, query_vector: Vector, result_vectors: Sequence[Vector]) -> list[list[float]]:
        if not result_vectors:
            return []
        lengths = [space.length for space in self._query_descriptor.index._spaces]
        all_vectors = list(result_vectors) + [query_vector]
        vectors_parts = [[part.value for part in vector.split(lengths)] for vector in all_vectors]
        vector_parts_per_space = [
            np.array([vectors_part[i] for vectors_part in vectors_parts]) for i in range(len(lengths))
        ]
        result_count = len(result_vectors)
        per_space_scores = [
            list[float](
                np.dot(
                    vector_parts[:result_count],
                    vector_parts[result_count],  # type: ignore[call-overload] # it exists
                ),
            )
            for vector_parts in vector_parts_per_space
        ]
        return [[scores[i] for scores in per_space_scores] for i in range(result_count)]

    def __check_executor_has_index(self) -> None:
        if self._query_descriptor.index not in self.app._indices:
            raise InvalidInputException(
                f"Query index {self._query_descriptor.index} is not amongst "
                + f"the executor's indices {self.app._indices}"
            )
