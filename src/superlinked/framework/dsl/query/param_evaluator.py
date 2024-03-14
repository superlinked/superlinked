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

from typing import Any

from superlinked.framework.common.const import DEFAULT_WEIGHT
from superlinked.framework.common.exception import QueryException
from superlinked.framework.dsl.query.param import FloatParamType, Param
from superlinked.framework.dsl.query.predicate.binary_predicate import BinaryPredicate
from superlinked.framework.dsl.query.predicate.evaluated_binary_predicate import (
    EvaluatedBinaryPredicate,
)

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["ParamEvaluator"] = False


class ParamEvaluator:
    def __init__(self, params: dict[str, Any]) -> None:
        self.params = params

    def evaluate_filters(
        self,
        filters: list[BinaryPredicate],
    ) -> list[EvaluatedBinaryPredicate]:
        return [
            self._evaluate_binary_predicate(query_filter) for query_filter in filters
        ]

    def evaluate_weight_param(
        self,
        param: FloatParamType,
        default: float = DEFAULT_WEIGHT,
    ) -> float:
        value = self._evaluate_param(param, default)
        if value is None:
            return default
        if isinstance(value, (float, int)):
            return float(value)
        raise QueryException(
            f"Weight should be numeric, got {value.__class__.__name__}"
        )

    def _evaluate_binary_predicate(
        self, predicate: BinaryPredicate
    ) -> EvaluatedBinaryPredicate:
        return EvaluatedBinaryPredicate(
            predicate,
            self.evaluate_weight_param(predicate.weight_param),
            self._evaluate_param(predicate.right_param),
        )

    def _evaluate_param(
        self, param: Param | int | str | float | None, default_value: Any = None
    ) -> int | str | float | None:
        if isinstance(param, Param):
            if param.name in self.params:
                return self.params[param.name]
            if default_value is not None:
                return default_value
            raise QueryException(
                f"Though parameter '{param.name}' was defined in "
                + "the query, its value was not provided. "
                + "Set it properly or register a new query."
            )
        return param
