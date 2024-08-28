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

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from beartype.typing import Sequence

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperand,
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    EvaluatedBinaryPredicate,
    LooksLikePredicate,
    SimilarPredicate,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator
from superlinked.framework.dsl.query.query_param_information import (
    ParamInfo,
    QueryParamInformation,
    WeightedParamInfo,
)
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["HardFilterInformation"] = False
__pdoc__["SimilarFilterInformation"] = False
__pdoc__["LooksLikeFilterInformation"] = False
__pdoc__["QueryFilterInformation"] = False


@dataclass(frozen=True)
class HardFilterInformation:
    op: ComparisonOperationType
    operand: ComparisonOperand[SchemaField]
    group_key: int | None
    param_name: str

    def evaluate(
        self, hard_filter_params: Sequence[ParamInfo]
    ) -> ComparisonOperation[SchemaField] | None:
        matching_params = [
            hard_filter_param
            for hard_filter_param in hard_filter_params
            if hard_filter_param.name == self.param_name
        ]
        if not matching_params:
            raise QueryException(
                "Query contains filter param without having filter clause."
            )
        hard_filter_param = matching_params[0]
        value = hard_filter_param.value
        if value is None:
            return None
        operation = ComparisonOperation(self.op, self.operand, value, self.group_key)
        QueryFilterValidator.validate_operation_operand_type(
            operation, allow_param=False
        )
        return operation


@dataclass(frozen=True)
class SimilarFilterInformation:
    space: Space
    schema_field: SchemaField
    value_param_name: str

    def evaluate(
        self, similar_filter_params: Sequence[WeightedParamInfo]
    ) -> tuple[Space, EvaluatedBinaryPredicate[SimilarPredicate]] | None:
        matching_params = [
            similar_filter_param
            for similar_filter_param in similar_filter_params
            if similar_filter_param.value_param.name == self.value_param_name
        ]
        if not matching_params:
            raise QueryException(
                "Query contains similar param without having similar clause."
            )
        similar_filter_param = matching_params[0]
        value = similar_filter_param.value_param.value
        if value is None:
            return None
        weight = get_weight(similar_filter_param.weight_param)
        node = self.space._get_node(self.schema_field.schema_obj)
        similar_filter = EvaluatedBinaryPredicate(
            SimilarPredicate(self.schema_field, value, weight, node)
        )
        return self.space, similar_filter


@dataclass(frozen=True)
class LooksLikeFilterInformation:
    schema_field: SchemaField

    def evaluate(
        self, looks_like_filter_param: WeightedParamInfo | None
    ) -> EvaluatedBinaryPredicate[LooksLikePredicate] | None:
        if looks_like_filter_param is None:
            raise QueryException(
                "Query contains with_vector param without having with_vector clause."
            )
        value = looks_like_filter_param.value_param.value
        weight = get_weight(looks_like_filter_param.weight_param)
        if value is None or weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT:
            return None
        expected_type = GenericClassUtil.get_single_generic_type(self.schema_field)
        if not isinstance(value, expected_type):
            raise QueryException(
                f"Unsupported with_vector operand type: {type(value).__name__}, expected {expected_type.__name__}."
            )
        looks_like_filter = EvaluatedBinaryPredicate(
            LooksLikePredicate(self.schema_field, value, weight)
        )
        return looks_like_filter


@dataclass(frozen=True)
class QueryFilterInformation:
    hard_filter_infos: list[HardFilterInformation] = field(default_factory=list)
    similar_filter_infos: list[SimilarFilterInformation] = field(default_factory=list)
    looks_like_filter_info: LooksLikeFilterInformation | None = None

    def alter(
        self,
        hard_filter_infos: list[HardFilterInformation] | None = None,
        similar_filter_infos: list[SimilarFilterInformation] | None = None,
        looks_like_filter_info: LooksLikeFilterInformation | None = None,
    ) -> QueryFilterInformation:
        return QueryFilterInformation(
            hard_filter_infos or self.hard_filter_infos,
            similar_filter_infos or self.similar_filter_infos,
            looks_like_filter_info or self.looks_like_filter_info,
        )

    def get_hard_filters(
        self, query_param_info: QueryParamInformation
    ) -> list[ComparisonOperation[SchemaField]]:
        hard_filters = [
            hard_filter_info.evaluate(query_param_info.hard_filter_params)
            for hard_filter_info in self.hard_filter_infos
        ]
        return [hard_filter for hard_filter in hard_filters if hard_filter is not None]

    def get_similar_filters(
        self, query_param_info: QueryParamInformation
    ) -> dict[Space, list[EvaluatedBinaryPredicate[SimilarPredicate]]]:
        similar_filters_by_space = defaultdict(list)
        for similar_filter_info in self.similar_filter_infos:
            space_and_similar_filter = similar_filter_info.evaluate(
                query_param_info.similar_filter_params
            )
            if space_and_similar_filter is not None:
                space, similar = space_and_similar_filter
                similar_filters_by_space[space].append(similar)
        return dict(similar_filters_by_space)

    def get_looks_like_filter(
        self, query_param_info: QueryParamInformation
    ) -> EvaluatedBinaryPredicate[LooksLikePredicate] | None:
        return (
            self.looks_like_filter_info.evaluate(
                query_param_info.looks_like_filter_param
            )
            if self.looks_like_filter_info
            else None
        )


def get_weight(weight_param: ParamInfo) -> float:
    weight = (
        weight_param.value
        if weight_param.value is not None
        else constants.DEFAULT_NOT_AFFECTING_WEIGHT
    )
    if not isinstance(weight, (int, float)):
        raise QueryException(
            f"{weight_param.name} should be numeric, got {type(weight).__name__}"
        )
    return float(weight)
