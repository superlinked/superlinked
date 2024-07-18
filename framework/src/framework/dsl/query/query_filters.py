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
from functools import reduce

from beartype.typing import Mapping, Sequence, cast

from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.exception import QueryException
from superlinked.framework.dsl.query.predicate.binary_op import BinaryOp
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    EvaluatedBinaryPredicate,
    LooksLikePredicate,
    SimilarPredicate,
)
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryFilters"] = False

SUPPORTED_BINARY_OPS = {BinaryOp.SIMILAR, BinaryOp.LOOKS_LIKE}


class QueryFilters:
    def __init__(
        self,
        looks_like_filter: EvaluatedBinaryPredicate[LooksLikePredicate] | None,
        similar_filters_by_space: Mapping[
            Space, Sequence[EvaluatedBinaryPredicate[SimilarPredicate]]
        ],
    ) -> None:
        self.__looks_like_filter = looks_like_filter
        self.__similar_filters_by_space = similar_filters_by_space
        self.__space_by_similar_filter: (
            dict[EvaluatedBinaryPredicate[SimilarPredicate], Space] | None
        ) = None
        self.__similar_filters_by_schema_field_node: (
            dict[SchemaFieldNode, Sequence[EvaluatedBinaryPredicate[SimilarPredicate]]]
            | None
        ) = None
        self.__similar_filters: Sequence[EvaluatedBinaryPredicate[SimilarPredicate]] = (
            reduce(
                lambda acc, ele: list(acc) + list(ele),
                self.__similar_filters_by_space.values(),
                [],
            )
        )
        self._check_all_filter_weight_is_not_zero()

    @property
    def looks_like_filter(self) -> EvaluatedBinaryPredicate[LooksLikePredicate] | None:
        return self.__looks_like_filter

    @property
    def space_by_similar_filter(
        self,
    ) -> dict[EvaluatedBinaryPredicate[SimilarPredicate], Space]:
        if self.__space_by_similar_filter is None:
            self.__space_by_similar_filter = {
                similar_filter: space
                for space, similar_filters in self.__similar_filters_by_space.items()
                for similar_filter in similar_filters
            }
        return self.__space_by_similar_filter

    @property
    def similar_filters_by_schema_field_node(
        self,
    ) -> dict[SchemaFieldNode, Sequence[EvaluatedBinaryPredicate[SimilarPredicate]]]:
        if self.__similar_filters_by_schema_field_node is None:
            similar_filters_by_schema_field_node = defaultdict(list)
            for similar_filter in self.__similar_filters:
                embedding_node = similar_filter.predicate.left_param_node
                schema_field_node = cast(
                    SchemaFieldNode | None,
                    embedding_node.find_ancestor(SchemaFieldNode),
                )
                if schema_field_node is not None:
                    similar_filters_by_schema_field_node[schema_field_node].append(
                        similar_filter
                    )
            self.__similar_filters_by_schema_field_node = dict(
                similar_filters_by_schema_field_node
            )
        return self.__similar_filters_by_schema_field_node

    @property
    def similar_filters(
        self,
    ) -> Sequence[EvaluatedBinaryPredicate[SimilarPredicate]]:
        return self.__similar_filters

    def _check_all_filter_weight_is_not_zero(self) -> None:
        all_filters: list[EvaluatedBinaryPredicate] = list(self.similar_filters) + (
            [self.looks_like_filter] if self.looks_like_filter else []
        )

        if all_filters and all(filter_.weight == 0 for filter_ in all_filters):
            raise QueryException("At least one filter needs to have a non-zero weight.")

    def has_multiple_similar_for_same_schema_field_node(self) -> bool:
        """
        Checks if there are multiple 'similar' filters for the schema field.
        We temporarily handle this use case separately, until we revamp the the query executor.
        """
        return any(
            len(similar_filters) > 1
            for similar_filters in self.similar_filters_by_schema_field_node.values()
        )

    def _get_weight_abs_sum(self, global_space_weight_map: dict[Space, float]) -> float:
        """Absolute value is needed for the case when the sum of weights would be zero."""
        weight_sum = self._get_similar_weight_abs_sum(global_space_weight_map)
        if self.looks_like_filter:
            weight_sum += abs(self.looks_like_filter.weight)
        return weight_sum

    def _get_similar_weight_abs_sum(
        self, global_space_weight_map: dict[Space, float]
    ) -> float:
        if self.has_multiple_similar_for_same_schema_field_node():
            weight_sum = sum(
                abs(similar.weight * global_space_weight_map.get(space, 1))
                for space, similar_filters in self.__similar_filters_by_space.items()
                for similar in similar_filters
            )
        else:
            weight_sum = sum(abs(filter_.weight) for filter_ in self.similar_filters)
        return weight_sum
