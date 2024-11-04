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

from abc import abstractmethod
from dataclasses import dataclass, replace

from beartype.typing import Any, Generic, TypeVar, cast
from typing_extensions import Self, override

from superlinked.framework.common.const import constants
from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.param import (
    UNSET_PARAM_NAME,
    Param,
    ParamInputType,
)
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    EvaluatedBinaryPredicate,
    LooksLikePredicate,
    SimilarPredicate,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

EvaluatedQueryT = TypeVar("EvaluatedQueryT")


@dataclass(frozen=True)
class QueryClause(Generic[EvaluatedQueryT]):
    value_param: Param | Evaluated[Param]

    def __post_init__(self) -> None:
        self._set_param_name_if_unset()

    def alter_value(self, params: dict[str, Any], is_override_set: bool) -> Self:
        if is_override_set or not isinstance(self.value_param, Evaluated):
            param_to_alter = self.get_param(self.value_param)
            if (value := params.get(param_to_alter.name)) is not None:
                return replace(self, value_param=Evaluated(param_to_alter, value))
        return self

    @abstractmethod
    def evaluate(self) -> EvaluatedQueryT: ...

    @abstractmethod
    def get_default_value_param_name(self) -> str: ...

    def get_value(self) -> PythonTypes | None:
        return self.get_param_value(self.value_param)

    def get_param_value(self, param: Param | Evaluated[Param]) -> PythonTypes | None:
        if isinstance(param, Evaluated):
            if param.value is None:
                return param.item.default
            return param.value
        return param.default

    def get_param(self, param: Param | Evaluated[Param]) -> Param:
        return param.item if isinstance(param, Evaluated) else param

    def _set_param_name_if_unset(self) -> None:
        if (value_param := self.get_param(self.value_param)).name is UNSET_PARAM_NAME:
            value_param.name = self.get_default_value_param_name()


QueryClauseT = TypeVar("QueryClauseT", bound=QueryClause)


@dataclass(frozen=True)
class WeightedQueryClause(QueryClause[EvaluatedQueryT]):
    weight_param: Param | Evaluated[Param]

    def alter_weight(self, params: dict[str, Any], is_override_set: bool) -> Self:
        if is_override_set or not isinstance(self.weight_param, Evaluated):
            param_to_alter = self.get_param(self.weight_param)
            if (weight := params.get(param_to_alter.name)) is not None:
                return replace(self, weight_param=Evaluated(param_to_alter, weight))
        return self

    def get_weight(self) -> float:
        weight = self.get_param_value(self.weight_param)
        if weight is None:
            weight = constants.DEFAULT_WEIGHT
        if not isinstance(weight, (int, float)):
            raise QueryException(
                f"Clause weight should be numeric, got {type(weight).__name__}."
            )
        return float(weight)

    @abstractmethod
    def get_default_weight_param_name(self) -> str: ...

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        if (weight_param := self.get_param(self.weight_param)).name is UNSET_PARAM_NAME:
            weight_param.name = self.get_default_weight_param_name()


@dataclass(frozen=True)
class SpaceWeightClause(QueryClause[tuple[Space, float]]):
    space: Space

    @override
    def get_value(self) -> float:
        if (value := super().get_value()) is not None:
            if not isinstance(value, (int, float)):
                raise QueryException(
                    f"Space weight should be numeric, got {type(value).__name__}."
                )
            return float(value)
        return constants.DEFAULT_NOT_AFFECTING_WEIGHT

    @override
    def evaluate(self) -> tuple[Space, float]:
        return self.space, self.get_value()

    @override
    def get_default_value_param_name(self) -> str:
        return f"space_weight_{type(self.space).__name__}_{str(hash(self.space))}_param"


@dataclass(frozen=True)
class LooksLikeFilterClause(
    WeightedQueryClause[EvaluatedBinaryPredicate[LooksLikePredicate] | None]
):
    schema_field: SchemaField

    @override
    def evaluate(self) -> EvaluatedBinaryPredicate[LooksLikePredicate] | None:
        value = self.get_value()
        weight = self.get_weight()
        if value is None or weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT:
            return None
        looks_like_filter = EvaluatedBinaryPredicate(
            LooksLikePredicate(self.schema_field, cast(ParamInputType, value), weight)
        )
        return looks_like_filter

    @override
    def get_default_value_param_name(self) -> str:
        return f"with_vector_{self.schema_field.name}_value_param"

    @override
    def get_default_weight_param_name(self) -> str:
        return f"with_vector_{self.schema_field.name}_weight_param"


@dataclass(frozen=True)
class SimilarFilterClause(
    WeightedQueryClause[tuple[Space, EvaluatedBinaryPredicate[SimilarPredicate]] | None]
):
    field_set: SpaceFieldSet
    # TODO [FAI-2453] remove this!
    schema_field: SchemaField

    @property
    def space(self) -> Space:
        return self.field_set.space

    @override
    def evaluate(
        self,
    ) -> tuple[Space, EvaluatedBinaryPredicate[SimilarPredicate]] | None:
        value = self.get_value()
        weight = self.get_weight()
        if value is None or weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT:
            return None
        node = self.space._get_embedding_node(self.schema_field.schema_obj)
        similar_filter = EvaluatedBinaryPredicate(
            SimilarPredicate(
                self.schema_field, cast(ParamInputType, value), weight, node
            )
        )
        return self.space, similar_filter

    @override
    def get_default_value_param_name(self) -> str:

        return f"similar_filter_{str(self.space)}_{self.schema_field.name}_value_param"

    @override
    def get_default_weight_param_name(self) -> str:
        return f"similar_filter_{str(self.space)}_{self.schema_field.name}_weight_param"


@dataclass(frozen=True)
class HardFilterClause(QueryClause[ComparisonOperation[SchemaField] | None]):
    op: ComparisonOperationType
    operand: SchemaField
    group_key: int | None

    @override
    def get_default_value_param_name(self) -> str:
        return f"hard_filter_{self.operand.name}_{self.op.value}_param"

    @override
    def evaluate(self) -> ComparisonOperation[SchemaField] | None:
        value = self.get_value()
        if value is None:
            return None
        operation = ComparisonOperation(self.op, self.operand, value, self.group_key)
        QueryFilterValidator.validate_operation_operand_type(
            operation, allow_param=False
        )
        return operation


@dataclass(frozen=True)
class NLQClause(QueryClause[str | None]):
    client_config: OpenAIClientConfig

    @override
    def get_default_value_param_name(self) -> str:
        return "natural_query_param"

    @override
    def evaluate(
        self,
    ) -> str | None:
        value = self.get_value()
        if value is not None and not isinstance(value, str):
            raise QueryException(
                f"NLQ prompt should be str, got {type(value).__name__}."
            )
        return value


@dataclass(frozen=True)
class LimitClause(QueryClause[int]):

    @override
    def get_default_value_param_name(self) -> str:
        return "limit_param"

    @override
    def get_value(self) -> int:
        if (value := super().get_value()) is not None:
            if not isinstance(value, int):
                raise QueryException(
                    f"Limit should be int, got {type(value).__name__}."
                )
            return value
        return constants.DEFAULT_LIMIT

    @override
    def evaluate(self) -> int:
        return self.get_value()


@dataclass(frozen=True)
class RadiusClause(QueryClause[float | None]):
    @override
    def get_default_value_param_name(self) -> str:
        return "radius_param"

    @override
    def get_value(self) -> float | None:
        if (value := super().get_value()) is not None:
            if not isinstance(value, int | float):
                raise QueryException(
                    f"Radius should be numeric, got {type(value).__name__}."
                )
            return float(value)
        return None

    @override
    def evaluate(self) -> float | None:
        return self.get_value()


@dataclass(frozen=True)
class OverriddenNowClause(QueryClause[int | None]):

    @override
    def get_default_value_param_name(self) -> str:
        return "overridden_now_param"

    @override
    def evaluate(self) -> int | None:
        if (value := self.get_value()) is not None:
            if not isinstance(value, int):
                raise QueryException(
                    f"'now' should be int, got {type(value).__name__}."
                )
            return value
        return None
