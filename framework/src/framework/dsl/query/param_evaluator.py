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

from beartype.typing import Any, Sequence, cast

from superlinked.framework.common.const import DEFAULT_LIMIT, DEFAULT_WEIGHT
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.param import (
    IntParamType,
    NumericParamType,
    Param,
    ParamInputType,
    ParamType,
)
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    BPT,
    EvaluatedBinaryPredicate,
)

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["ParamEvaluator"] = False


class ParamEvaluator:
    def __init__(self, params: dict[str, Any]) -> None:
        self.params = params

    def evaluate_weight_param(
        self,
        param: NumericParamType,
        default: float = DEFAULT_WEIGHT,
    ) -> float:
        value = self.evaluate_numeric_param(param, "Weight")
        if value is None:
            return default
        return value

    def evaluate_radius_param(
        self,
        param: NumericParamType | None,
    ) -> float | None:
        value = self.evaluate_numeric_param(param, "Radius")
        if value is not None and (value > 1 or value < 0):
            raise ValueError(
                f"Not a valid Radius value ({value}). It should be between 0 and 1."
            )
        return value

    def evaluate_hard_filters_param(
        self,
        hard_filters: Sequence[ComparisonOperation[SchemaField]],
    ) -> Sequence[ComparisonOperation[SchemaField]]:
        return [
            ComparisonOperation(
                hard_filter._op, hard_filter._operand, self._evaluate_param(param)
            )
            for hard_filter in hard_filters
            if self.is_param_defined(param := cast(ParamType, hard_filter._other))
        ]

    def evaluate_numeric_param(
        self,
        param: NumericParamType | None,
        param_name: str,
    ) -> float | None:
        value = self._evaluate_param(param)
        if value is None:
            return value
        if isinstance(value, (float, int)):
            return float(value)
        raise QueryException(
            f"{param_name} should be numeric, got {value.__class__.__name__}"
        )

    def evaluate_limit_param(
        self,
        param: IntParamType | None,
    ) -> int:
        value = self._evaluate_param(param)
        if value is None:
            return DEFAULT_LIMIT
        if not isinstance(value, int):
            raise QueryException(f"Limit should be int, got {value.__class__.__name__}")
        return value

    def evaluate_binary_predicate(
        self, predicate: BPT
    ) -> EvaluatedBinaryPredicate[BPT]:
        return EvaluatedBinaryPredicate(
            predicate,
            self.evaluate_weight_param(predicate.weight_param),
            self._evaluate_param(predicate.right_param, True),
        )

    def is_param_defined(
        self,
        param: ParamType,
    ) -> bool:
        return not isinstance(param, Param) or cast(Param, param).name in self.params

    def _evaluate_param(
        self, param: ParamType, raise_if_none: bool = False
    ) -> ParamInputType:
        if isinstance(param, Param):
            evaluated_param = self.params.get(param.name)
            if raise_if_none and evaluated_param is None:
                raise QueryException(
                    f"Though parameter '{param.name}' was defined in "
                    + "the query, its value was not provided. "
                    + "Set it properly or register a new query."
                )
            return evaluated_param
        return param
