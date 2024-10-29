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


from functools import partial

import structlog
from beartype.typing import Any, Sequence

from superlinked.framework.common.dag.context import (
    CONTEXT_COMMON,
    CONTEXT_COMMON_NOW,
    ExecutionContext,
    ExecutionEnvironment,
    NowStrategy,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.knn_search_params import (
    KNNSearchParams,
)
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.dsl.executor.executor import App
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor
from superlinked.framework.dsl.query.query_filters import QueryFilters
from superlinked.framework.dsl.query.query_param_value_setter import (
    QueryParamValueSetter,
)
from superlinked.framework.dsl.query.query_vector_factory import QueryVectorFactory
from superlinked.framework.dsl.query.result import Result, ResultEntry

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
            evaluator: An instance of the QueryDagEvaluator class used to evaluate the query.
        """
        self.app = app
        self._query_descriptor = query_descriptor
        self.query_vector_factory = query_vector_factory
        self._logger = logger.bind(schema=self._query_descriptor.schema._schema_name)

    def query(self, **params: Any) -> Result:
        """
        Execute a query with keyword parameters.

        Args:
            **params: Arbitrary arguments with keys corresponding to the `name` attribute of the `Param` instance.

        Returns:
            Result: The result of the query execution that can be inspected and post-processed.

        Raises:
            QueryException: If the query index is not amongst the executor's indices.
        """
        self.__check_executor_has_index()
        query_descriptor = QueryParamValueSetter.set_values(
            self._query_descriptor, params
        )
        knn_search_params = self._produce_knn_search_params(query_descriptor)
        entities: Sequence[SearchResultItem] = self._knn_search(
            knn_search_params, query_descriptor
        )
        self._logger.info(
            "executed query",
            n_results=len(entities),
            limit=knn_search_params.limit,
            radius=knn_search_params.radius,
            pii_knn_params=params,
            pii_query_vector=partial(str, knn_search_params.vector),
        )
        return Result(
            self._map_entities_to_result_entries(query_descriptor.schema, entities),
            query_descriptor,
        )

    def _produce_knn_search_params(
        self, query_descriptor: QueryDescriptor
    ) -> KNNSearchParams:
        limit = query_descriptor.get_limit()
        radius = query_descriptor.get_radius()
        hard_filters = query_descriptor.get_hard_filters()
        query_vector = self._produce_query_vector(query_descriptor)
        return KNNSearchParams(query_vector, limit, hard_filters, radius)

    def _produce_query_vector(self, query_descriptor: QueryDescriptor) -> Vector:
        query_filters = self._get_query_filters(query_descriptor)
        weight_by_space = query_descriptor.get_weights_by_space()
        context = self._create_query_context_base(query_descriptor)
        query_node_inputs_by_node_id = (
            query_descriptor.calculate_query_node_inputs_by_node_id()
        )
        return self.query_vector_factory.produce_vector(
            query_descriptor.index._node_id,
            query_node_inputs_by_node_id,
            query_filters,
            weight_by_space,
            query_descriptor.schema,
            context,
        )

    def _get_query_filters(self, query_descriptor: QueryDescriptor) -> QueryFilters:
        return QueryFilters(
            query_descriptor.get_looks_like_filter(),
            query_descriptor.get_similar_filters(),
        )

    def _create_query_context_base(
        self, query_descriptor: QueryDescriptor
    ) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY,
            data=self.app._context.data,
            now_strategy=NowStrategy.CONTEXT_TIME,
        )
        context_time = query_descriptor.get_context_time(self.app._context.now())
        eval_context.update_data({CONTEXT_COMMON: {CONTEXT_COMMON_NOW: context_time}})
        return eval_context

    def _knn_search(
        self, knn_search_params: KNNSearchParams, query_descriptor: QueryDescriptor
    ) -> Sequence[SearchResultItem]:
        return self.app.storage_manager.knn_search(
            query_descriptor.index._node, query_descriptor.schema, [], knn_search_params
        )

    def _map_entities_to_result_entries(
        self, schema: IdSchemaObject, result_items: Sequence[SearchResultItem]
    ) -> Sequence[ResultEntry]:
        return [
            ResultEntry(
                entity,
                self._get_stored_object_or_raise(
                    schema, entity.header.origin_id or entity.header.object_id
                ),
            )
            for entity in result_items
        ]

    def _get_stored_object_or_raise(
        self, schema: IdSchemaObject, object_id: str
    ) -> dict[str, Any]:
        stored_object = self.app.storage_manager.read_object_json(schema, object_id)
        if not stored_object:
            raise QueryException(
                f"No stored {schema._schema_name} object found for the given object_id: {object_id}"
            )
        return stored_object

    def __check_executor_has_index(self) -> None:
        if self._query_descriptor.index not in self.app._indices:
            raise QueryException(
                f"Query index {self._query_descriptor.index} is not amongst "
                + f"the executor's indices {self.app._indices}"
            )
