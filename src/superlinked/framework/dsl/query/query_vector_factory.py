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

from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from math import sqrt

from beartype.typing import Sequence

from superlinked.framework.common.dag.context import (
    ExecutionContext,
    ExecutionEnvironment,
    NowStrategy,
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
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    EvaluatedBinaryPredicate,
    SimilarPredicate,
)
from superlinked.framework.dsl.query.query_filters import QueryFilters
from superlinked.framework.dsl.query.query_weighting import QueryWeighting
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.evaluator.query_dag_evaluator import QueryDagEvaluator

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryVectorFactory"] = False


@dataclass(frozen=True)
class SimilarEvaluationInput:
    node_id_weight_map: dict[str, float]
    parsed_schema_fields: Sequence[ParsedSchemaField]


class QueryVectorFactory:
    def __init__(
        self,
        dag: Dag,
        schemas: set[SchemaObject],
        storage_manager: StorageManager,
    ) -> None:
        self._evaluator = QueryDagEvaluator(dag, schemas, storage_manager)
        self._storage_manager = storage_manager
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
        similar_vector = self._get_similar_vector(
            schema,
            query_filters,
            context_base,
            global_space_weight_map,
        )
        weight_sum = query_filters._get_weight_abs_sum(global_space_weight_map)
        # Aggregate them.
        vector: Vector = self._combine_vectors(
            [looks_like_vector, similar_vector],
            weight_sum,
        )
        if not query_filters.has_multiple_similar_for_same_schema_field_node():
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
            if _vector := self._storage_manager.read_node_result(
                looks_like_filter.predicate.left_param.schema_obj,
                str(looks_like_filter.value),
                index_node_id,
                Vector,
            ):
                return _vector * looks_like_filter.weight
            raise QueryException(
                f"Entity not found object_id: {looks_like_filter.value} node_id: {index_node_id}"
            )
        return None

    def _get_similar_vector(
        self,
        schema: IdSchemaObject,
        query_filters: QueryFilters,
        context_base: ExecutionContext,
        global_space_weight_map: dict[Space, float],
    ) -> Vector | None:
        if not (query_filters.similar_filters or not query_filters.looks_like_filter):
            return None
        node_id_weight_map = self.__get_node_id_weight_map_from_filters(query_filters)
        if query_filters.has_multiple_similar_for_same_schema_field_node():
            similar_evaluation_inputs = [
                self._calculate_similar_evaluation_inputs_for_same_node(
                    query_filters,
                    similar_filters_for_a_node,
                    similar_filter,
                    node_id_weight_map,
                    global_space_weight_map,
                )
                for similar_filters_for_a_node in query_filters.similar_filters_by_schema_field_node.values()
                for similar_filter in similar_filters_for_a_node
            ]
            weight_sum = query_filters._get_weight_abs_sum(global_space_weight_map)
        else:
            parsed_schema_fields = self._build_parsed_schema_fields(
                query_filters.similar_filters
            )
            similar_evaluation_inputs = [
                SimilarEvaluationInput(node_id_weight_map, parsed_schema_fields)
            ]
            weight_sum = 1
        evaluated_vectors: list[Vector | None] = [
            self.__evaluate_similar(schema, context_base, similar_evaluation_input)
            for similar_evaluation_input in similar_evaluation_inputs
        ]
        return self._combine_vectors(
            evaluated_vectors,
            weight_sum,
        )

    def __evaluate_similar(
        self,
        schema: IdSchemaObject,
        context_base: ExecutionContext,
        similar_evaluation_input: SimilarEvaluationInput,
    ) -> Vector | None:
        parsed_schema = ParsedSchema(
            schema, "", similar_evaluation_input.parsed_schema_fields
        )
        load_default_node_input = not similar_evaluation_input.parsed_schema_fields
        query_context = self._create_query_context(
            context_base,
            similar_evaluation_input.node_id_weight_map,
            load_default_node_input,
        )
        return self._evaluator.evaluate_single(
            parsed_schema,
            query_context,
        ).main.value

    def _calculate_similar_evaluation_inputs_for_same_node(
        self,
        query_filters: QueryFilters,
        similar_filters_for_a_node: Sequence[
            EvaluatedBinaryPredicate[SimilarPredicate]
        ],
        similar_filter: EvaluatedBinaryPredicate[SimilarPredicate],
        default_node_id_weight_map: dict[str, float],
        global_space_weight_map: dict[Space, float],
    ) -> SimilarEvaluationInput:
        return SimilarEvaluationInput(
            node_id_weight_map=self.__get_node_id_weight_map_for_same_node(
                global_space_weight_map,
                default_node_id_weight_map,
                similar_filter,
                query_filters.space_by_similar_filter[similar_filter],
            ),
            parsed_schema_fields=self.__build_parsed_schema_fields_for_same_node(
                [
                    other_similar_filter
                    for other_similar_filter in query_filters.similar_filters
                    if other_similar_filter not in similar_filters_for_a_node
                ]
                + [similar_filter]
            ),
        )

    def _create_query_context(
        self,
        context_base: ExecutionContext,
        node_id_weight_map: dict[str, float],
        load_default_node_input: bool = False,
    ) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY,
            data=context_base.data,
            now_strategy=NowStrategy.CONTEXT_TIME,
        )
        eval_context.update_data(
            self._query_weighting.get_node_weights(node_id_weight_map)
        )
        eval_context.set_load_default_node_input(load_default_node_input)
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
        similar_filters: Sequence[EvaluatedBinaryPredicate[SimilarPredicate]],
    ) -> list[ParsedSchemaField]:
        return [
            ParsedSchemaField.from_schema_field(
                filter_.predicate.left_param, filter_.value
            )
            for filter_ in similar_filters
        ]

    @staticmethod
    def _combine_vectors(vectors: list[Vector | None], weight_sum: float) -> Vector:
        if non_none_vectors := [
            vector for vector in vectors if vector and not vector.is_empty
        ]:
            aggregation = reduce(lambda a, b: a.aggregate(b), non_none_vectors)
            return aggregation.normalize(sqrt(weight_sum))
        raise QueryException("No implemented OP provided for the query")

    @staticmethod
    def __get_node_id_weight_map_from_filters(
        query_filters: QueryFilters,
    ) -> dict[str, float]:
        return {
            filter_.predicate.left_param_node.node_id: filter_.weight
            for filter_ in query_filters.similar_filters
        }

    @staticmethod
    def __build_parsed_schema_fields_for_same_node(
        similar_filters: list[EvaluatedBinaryPredicate[SimilarPredicate]],
    ) -> list[ParsedSchemaField[str]]:
        parsed_schema_fields_by_schema_field = defaultdict(list)
        for parsed_schema_field in QueryVectorFactory._build_parsed_schema_fields(
            similar_filters
        ):
            parsed_schema_fields_by_schema_field[
                parsed_schema_field.schema_field
            ].append(parsed_schema_field.value)
        return [
            ParsedSchemaField(schema_field, schema_field.combine_values(values))
            for schema_field, values in parsed_schema_fields_by_schema_field.items()
        ]

    @staticmethod
    def __get_node_id_weight_map_for_same_node(
        global_space_weight_map: dict[Space, float],
        default_node_id_weight_map: dict[str, float],
        similar: EvaluatedBinaryPredicate[SimilarPredicate],
        affected_space: Space,
    ) -> dict[str, float]:
        actual_weights = default_node_id_weight_map.copy()
        new_weight = similar.weight * global_space_weight_map.get(affected_space, 1)
        actual_weights[similar.predicate.left_param_node.node_id] = new_weight
        return actual_weights
