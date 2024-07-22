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

from beartype.typing import Any, Mapping, Sequence, cast

from superlinked.framework.common.const import (
    DEFAULT_LIMIT,
    DEFAULT_NOT_AFFECTING_WEIGHT,
)
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperand,
    ComparisonOperation,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.natural_language_query_param_handler import (
    EvaluatedParam,
    NaturalLanguageQueryParams,
    WeightedEvaluatedParam,
)
from superlinked.framework.dsl.query.param import (
    IntParamType,
    NumericParamType,
    Param,
    ParamInputType,
    ParamType,
)
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    BPT,
    BinaryPredicate,
    EvaluatedBinaryPredicate,
    LooksLikePredicate,
    SimilarPredicate,
)
from superlinked.framework.dsl.query.query import QueryObj
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["ParamEvaluator"] = False


@dataclass
class EvaluatedParamInfo:
    limit: int
    radius: float | None
    space_weight_map: dict[Space, float]
    hard_filters: list[ComparisonOperation[SchemaField]]
    similar_filters: dict[Space, list[EvaluatedBinaryPredicate[SimilarPredicate]]]
    looks_like_filter: EvaluatedBinaryPredicate[LooksLikePredicate] | None
    natural_language_query_params: NaturalLanguageQueryParams


class ParamEvaluator:
    def __init__(
        self,
        params: dict[str, Any],
    ) -> None:
        self.params = params

    def evaluate_params(self, query_obj: QueryObj) -> EvaluatedParamInfo:
        natural_language_query_params = self._evaluate_natural_language_params(
            query_obj
        )
        limit = self._evaluate_limit_param(query_obj.limit_)
        radius = self._evaluate_radius_param(query_obj.radius_)
        space_weight_map = self._calculate_space_weight_map(
            natural_language_query_params.weight_param_by_space
        )
        hard_filters = self._calculate_evaluated_hard_filters(
            query_obj.hard_filters,
            natural_language_query_params.hard_filter_param_by_schema_field,
        )
        similar_filters = self._calculate_similar_filters_by_space(
            query_obj.similar_filters_by_space,
            natural_language_query_params.similar_filter_by_space_by_schema_field,
        )
        looks_like_filter = self._calculate_looks_like_filter(
            query_obj.looks_like_filter,
            natural_language_query_params.looks_like_filter_param,
        )
        return EvaluatedParamInfo(
            limit,
            radius,
            space_weight_map,
            hard_filters,
            similar_filters,
            looks_like_filter,
            natural_language_query_params,
        )

    def _evaluate_natural_language_params(
        self, query_obj: QueryObj
    ) -> NaturalLanguageQueryParams:
        weight_param_by_space = self._evaluate_space_weights(
            query_obj.builder.space_weight_map
        )
        hard_filter_param_by_schema_field = self._evaluate_hard_filters(
            query_obj.hard_filters
        )
        similar_filter_param_by_space_by_schema_field = self._evaluate_similar_filters(
            query_obj.similar_filters_by_space
        )
        looks_like_filter_param = self._evaluate_looks_like_filter(
            query_obj.looks_like_filter
        )
        return NaturalLanguageQueryParams(
            weight_param_by_space,
            hard_filter_param_by_schema_field,
            similar_filter_param_by_space_by_schema_field,
            looks_like_filter_param,
        )

    def _evaluate_space_weights(
        self, space_weight_map: dict[Space, NumericParamType]
    ) -> dict[Space, EvaluatedParam[float | None]]:
        return {
            space: self._calculate_weight_param_info(
                weight_param, f"{self._get_space_name(space)}space_weight"
            )
            for space, weight_param in space_weight_map.items()
        }

    def _evaluate_hard_filters(
        self, hard_filters: Sequence[ComparisonOperation[SchemaField]]
    ) -> dict[ComparisonOperand[SchemaField], EvaluatedParam[ParamInputType]]:
        return {
            hard_filter._operand: self._calculate_binary_param_info(
                cast(ParamType, hard_filter._other),
                f"{cast(SchemaField, hard_filter._operand).name}_{hard_filter._op.value}_filter_clause_value",
            )
            for hard_filter in hard_filters
        }

    def _evaluate_similar_filters(
        self, similar_filters_by_space: dict[Space, Sequence[SimilarPredicate]]
    ) -> dict[SchemaField, dict[Space, WeightedEvaluatedParam]]:
        similar_filter_by_schema_field_by_space: defaultdict[
            SchemaField, dict[Space, WeightedEvaluatedParam]
        ] = defaultdict(dict)
        for space, similar_filters in similar_filters_by_space.items():
            for similar_filter in similar_filters:
                similar_filter_by_schema_field_by_space[similar_filter.left_param][
                    space
                ] = self._calculate_weighted_evaluated_param(
                    similar_filter, "similar", space
                )
        return dict(similar_filter_by_schema_field_by_space)

    def _evaluate_looks_like_filter(
        self, looks_like_filter: LooksLikePredicate | None
    ) -> WeightedEvaluatedParam | None:
        return (
            self._calculate_weighted_evaluated_param(looks_like_filter, "with_vector")
            if looks_like_filter
            else None
        )

    def _calculate_weighted_evaluated_param(
        self, predicate: BinaryPredicate, clause_type: str, space: Space | None = None
    ) -> WeightedEvaluatedParam:
        field_name = str(predicate.left_param.name)
        return WeightedEvaluatedParam(
            value=self._calculate_binary_param_info(
                predicate.right_param,
                f"{self._get_space_name(space)}{field_name}_{clause_type}_clause_value",
            ),
            weight=self._calculate_weight_param_info(
                predicate.weight_param,
                f"{self._get_space_name(space)}{field_name}_{clause_type}_clause_weight",
            ),
        )

    def _calculate_weight_param_info(
        self, param: NumericParamType, default_name: str
    ) -> EvaluatedParam[float | None]:
        name, description = self._get_param_name_and_description(param, default_name)
        value = self._evaluate_numeric_param(param, name)
        return EvaluatedParam(name, description, value)

    def _calculate_binary_param_info(
        self, param: ParamType, default_name: str
    ) -> EvaluatedParam[ParamInputType]:
        name, description = self._get_param_name_and_description(param, default_name)
        value = self._evaluate_param(param)
        return EvaluatedParam(name, description, value)

    def _get_param_name_and_description(
        self, param: ParamType, default_name: str
    ) -> tuple[str, str | None]:
        if isinstance(param, Param):
            return param.name, param.description
        return default_name, None

    def _evaluate_radius_param(self, param: NumericParamType | None) -> float | None:
        value = self._evaluate_numeric_param(param, "Radius")
        if value is not None and (value > 1 or value < 0):
            raise ValueError(
                f"Not a valid Radius value ({value}). It should be between 0 and 1."
            )
        return value

    def _evaluate_numeric_param(
        self, param: NumericParamType | None, param_name: str
    ) -> float | None:
        value = self._evaluate_param(param)
        if value is None:
            return value
        if isinstance(value, (float, int)):
            return float(value)
        raise QueryException(
            f"{param_name} should be numeric, got {value.__class__.__name__}"
        )

    def _evaluate_limit_param(self, param: IntParamType | None) -> int:
        value = self._evaluate_param(param)
        if value is None:
            return DEFAULT_LIMIT
        if not isinstance(value, int):
            raise QueryException(f"Limit should be int, got {value.__class__.__name__}")
        return value

    def _evaluate_param(self, param: ParamType) -> ParamInputType:
        if isinstance(param, Param):
            return self.params.get(param.name)
        return param

    @classmethod
    def _get_space_name(cls, space: Space | None = None) -> str:
        if space is None:
            return ""
        return f"{space.__class__.__name__}_{hash(space)}_"

    @classmethod
    def _calculate_evaluated_hard_filters(
        cls,
        hard_filters: Sequence[ComparisonOperation[SchemaField]],
        hard_filter_param_by_schema_field: dict[
            ComparisonOperand[SchemaField], EvaluatedParam[ParamInputType]
        ],
    ) -> list[ComparisonOperation[SchemaField]]:
        return [
            ComparisonOperation(hard_filter._op, hard_filter._operand, value)
            for hard_filter in hard_filters
            if (value := hard_filter_param_by_schema_field[hard_filter._operand].value)
            is not None
        ]

    @classmethod
    def _calculate_similar_filters_by_space(
        cls,
        similar_filters_by_space: Mapping[Space, Sequence[SimilarPredicate]],
        similar_filter_by_space_by_schema_field: dict[
            SchemaField, dict[Space, WeightedEvaluatedParam]
        ],
    ) -> dict[Space, list[EvaluatedBinaryPredicate[SimilarPredicate]]]:
        return {
            space: [
                evaluated_similar_filter
                for evaluated_similar_filter in (
                    cls._calculate_evaluated_binary_predicate(
                        similar_filter,
                        similar_filter_by_space_by_schema_field[
                            similar_filter.left_param
                        ][space],
                    )
                    for similar_filter in similar_filters
                )
                if evaluated_similar_filter is not None
            ]
            for space, similar_filters in similar_filters_by_space.items()
        }

    @classmethod
    def _calculate_looks_like_filter(
        cls,
        looks_like_filter: LooksLikePredicate | None,
        looks_like_filter_param: WeightedEvaluatedParam | None,
    ) -> EvaluatedBinaryPredicate[LooksLikePredicate] | None:
        if looks_like_filter is None or looks_like_filter_param is None:
            if not (looks_like_filter is None and looks_like_filter_param is None):
                raise ValueError(
                    "If either of looks_like_filter or looks_like_filter_param is None,"
                    "then the other must be None too."
                )
            return None
        return cls._calculate_evaluated_binary_predicate(
            looks_like_filter, looks_like_filter_param
        )

    @classmethod
    def _calculate_space_weight_map(
        cls, weight_param_by_space: dict[Space, EvaluatedParam[float | None]]
    ) -> dict[Space, float]:
        return {
            space: (
                param.value if param.value is not None else DEFAULT_NOT_AFFECTING_WEIGHT
            )
            for space, param in weight_param_by_space.items()
        }

    @classmethod
    def _calculate_evaluated_binary_predicate(
        cls, predicate: BPT, weighted_evaluated_param: WeightedEvaluatedParam
    ) -> EvaluatedBinaryPredicate[BPT] | None:
        value = weighted_evaluated_param.value.value
        if value is None:
            return None
        weight = (
            weighted_evaluated_param.weight.value
            if weighted_evaluated_param.weight.value is not None
            else DEFAULT_NOT_AFFECTING_WEIGHT
        )
        return EvaluatedBinaryPredicate(predicate, weight, value)
