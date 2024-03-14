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

from functools import reduce
from typing import cast

from superlinked.framework.common.dag.context import (
    ExecutionContext,
    ExecutionEnvironment,
)
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.dsl.query.query_filters import QueryFilters
from superlinked.framework.dsl.query.query_weighting import QueryWeighting
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.evaluator.query_dag_evaluator import QueryDagEvaluator
from superlinked.framework.storage.entity import EntityId
from superlinked.framework.storage.entity_store_manager import EntityStoreManager

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryVectorFactory"] = False


class QueryVectorFactory:
    def __init__(
        self,
        dag: Dag,
        schemas: set[SchemaObject],
        entity_store_manager: EntityStoreManager,
    ) -> None:
        self._evaluator = QueryDagEvaluator(dag, schemas, entity_store_manager)
        self._entity_store_manager = entity_store_manager
        self._query_weighting = QueryWeighting(dag)

    def produce_vector(
        self,
        index_node_id: str,
        query_filters: QueryFilters,
        global_space_weight_map: dict[Space, float],
        schema: IdSchemaObject,
        context_base: ExecutionContext,
    ) -> Vector:
        # Generate vector from LOOKS_LIKE filters.
        looks_like_vector: Vector | None = self._get_looks_like_vector(
            index_node_id, query_filters
        )
        # Generate vector from SIMILAR filters.
        similar_vector: Vector | None = self._get_similar_vector(
            schema, query_filters, context_base
        )
        # Aggregate them.
        vector: Vector = QueryVectorFactory._combine_vectors(
            [looks_like_vector, similar_vector]
        )
        # Re-weight by space weights.
        space_node_id_weight_map: dict[str, float] = (
            self.__get_node_id_weight_map_from_space_weight_map(
                schema, global_space_weight_map
            )
        )
        query_context = self._create_query_context(
            context_base, space_node_id_weight_map
        )
        vector = self._evaluator.re_weight_vector(schema, vector, query_context)
        return vector

    def _get_looks_like_vector(
        self,
        index_node_id: str,
        query_filters: QueryFilters,
    ) -> Vector | None:
        if looks_like_filter := query_filters.looks_like_filter:
            # search by the vector of the referenced entity
            if _vector := self._entity_store_manager.get_vector(
                EntityId(
                    object_id=str(looks_like_filter.value),
                    node_id=index_node_id,
                    schema_id=looks_like_filter.predicate.left_param.schema_obj._schema_name,
                )
            ):
                return cast(Vector, _vector)

            raise QueryException(
                f"Entity not found object_id: {looks_like_filter.value} node_id: {index_node_id}"
            )
        return None

    def _get_similar_vector(
        self,
        schema: IdSchemaObject,
        query_filters: QueryFilters,
        context_base: ExecutionContext,
    ) -> Vector | None:
        if (
            similar_filters := query_filters.similar_filters
        ) or query_filters.filter_count == 0:
            query_context = self._create_query_context(
                context_base,
                QueryVectorFactory.__get_node_id_weight_map_from_filters(query_filters),
            )
            parsed_schema_fields = (
                self._build_parsed_schema_fields(query_filters)
                if similar_filters
                else []
            )
            parsed_schema = ParsedSchema(schema, "", parsed_schema_fields)
            evaluation = self._evaluator.evaluate(parsed_schema, query_context)
            return evaluation.main.value
        return None

    def _create_query_context(
        self,
        context_base: ExecutionContext,
        node_id_weight_map: dict[str, float],
    ) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY, data=context_base.data
        )
        eval_context.update_data(
            self._query_weighting.get_node_weights(node_id_weight_map)
        )
        return eval_context

    @staticmethod
    def __get_node_id_weight_map_from_space_weight_map(
        schema: IdSchemaObject, space_weight_map: dict[Space, float]
    ) -> dict[str, float]:
        return {
            space._get_node(schema).node_id: weight
            for space, weight in space_weight_map.items()
        }

    @staticmethod
    def _build_parsed_schema_fields(
        query_filters: QueryFilters,
    ) -> list[ParsedSchemaField]:
        return [
            ParsedSchemaField.from_schema_field(
                filter_.predicate.left_param, filter_.value
            )
            for filter_ in query_filters.similar_filters
        ]

    @staticmethod
    def _combine_vectors(vectors: list[Vector | None]) -> Vector:
        if non_none_vectors := [vector for vector in vectors if vector]:
            return reduce(lambda a, b: a.aggregate(b), non_none_vectors).normalize()
        raise QueryException("No implemented OP provided for the query")

    @staticmethod
    def __get_node_id_weight_map_from_filters(
        query_filters: QueryFilters,
    ) -> dict[str, float]:
        return {
            filter_.predicate.left_param_node.node_id: filter_.weight
            for filter_ in query_filters.similar_filters
            if filter_.predicate.left_param_node
        }
