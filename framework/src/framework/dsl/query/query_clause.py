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

from beartype.typing import Any, Generic, Mapping, Sequence, TypeVar, cast
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
from superlinked.framework.common.interface.has_annotation import HasAnnotation
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.query.param import (
    UNSET_PARAM_NAME,
    Param,
    ParamInputType,
)
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    EvaluatedBinaryPredicate,
    LooksLikePredicate,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

EvaluatedQueryT = TypeVar("EvaluatedQueryT")


@dataclass(frozen=True)
class QueryClause(Generic[EvaluatedQueryT]):
    value_param: Param | Evaluated[Param]

    def __post_init__(self) -> None:
        self._set_param_name_if_unset()

    @abstractmethod
    def evaluate(self) -> EvaluatedQueryT: ...

    @abstractmethod
    def get_default_value_param_name(self) -> str: ...

    @property
    def value_accepted_type(self) -> type:
        raise RuntimeError("This method should not be used.")

    @property
    def params(self) -> Sequence[Param | Evaluated[Param]]:
        return [self.value_param]

    @property
    def value_param_name(self) -> str:
        return self.get_param(self.value_param).name

    def alter_value(self, params: Mapping[str, ParamInputType], is_override_set: bool) -> Self:
        if (is_override_set or not isinstance(self.value_param, Evaluated)) and (
            value := params.get(self.value_param_name)
        ) is not None:
            param_to_alter = self.get_param(self.value_param)
            overridden_value = self._transform_param_value(value)
            return replace(self, value_param=param_to_alter.to_evaluated(overridden_value))
        return self

    def _transform_param_value(self, param_value: Any) -> Any:
        # * can be overridden in child classes
        return param_value

    def get_value(self) -> PythonTypes | None:
        value = self.get_param_value(self.value_param)
        return cast(PythonTypes | None, value)

    def get_allowed_values(self, param: Param | Evaluated[Param]) -> set[ParamInputType]:
        return self.get_param(param).options or set()

    @classmethod
    def get_param_value(cls, param: Param | Evaluated[Param]) -> ParamInputType | None:
        if isinstance(param, Evaluated):
            if param.value is None:
                return param.item.default
            return param.value
        return param.default

    @classmethod
    def get_param(cls, param: Param | Evaluated[Param]) -> Param:
        return param.item if isinstance(param, Evaluated) else param

    def _set_param_name_if_unset(self) -> None:
        if self.value_param_name is UNSET_PARAM_NAME:
            self.get_param(self.value_param).name = self.get_default_value_param_name()

    @classmethod
    def _format_param_options(cls, param: Param) -> str:
        return ", ".join(sorted(str(value) for value in param.options)) if param.options else ""


QueryClauseT = TypeVar("QueryClauseT", bound=QueryClause)


@dataclass(frozen=True)
class WeightedQueryClause(QueryClause[EvaluatedQueryT]):
    weight_param: Param | Evaluated[Param]

    def alter_weight(self, params: Mapping[str, ParamInputType], is_override_set: bool) -> Self:
        if (is_override_set or not isinstance(self.weight_param, Evaluated)) and (
            weight := params.get(self.weight_param_name)
        ) is not None:
            param_to_alter = self.get_param(self.weight_param)
            return replace(self, weight_param=param_to_alter.to_evaluated(weight))
        return self

    def get_weight(self) -> float:
        weight = self.get_param_value(self.weight_param)
        if weight is None:
            weight = constants.DEFAULT_WEIGHT
        if not isinstance(weight, (int, float)):
            raise QueryException(f"Clause weight should be numeric, got {type(weight).__name__}.")
        return float(weight)

    @abstractmethod
    def get_default_weight_param_name(self) -> str: ...

    @property
    @override
    def params(self) -> Sequence[Param | Evaluated[Param]]:
        return [self.value_param, self.weight_param]

    @property
    def weight_param_name(self) -> str:
        return self.get_param(self.weight_param).name

    @property
    def weight_accepted_type(self) -> type:
        return float

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        if self.weight_param_name is UNSET_PARAM_NAME:
            self.get_param(self.weight_param).name = self.get_default_weight_param_name()


@dataclass(frozen=True)
class SpaceWeightClause(QueryClause[tuple[Space, float]], HasAnnotation):
    space: Space

    @override
    def get_value(self) -> float:
        if (value := super().get_value()) is not None:
            if not isinstance(value, (int, float)):
                raise QueryException(f"Space weight should be numeric, got {type(value).__name__}.")
            return float(value)
        return constants.DEFAULT_NOT_AFFECTING_WEIGHT

    @override
    def evaluate(self) -> tuple[Space, float]:
        return self.space, self.get_value()

    @override
    def get_default_value_param_name(self) -> str:
        return f"space_weight_{type(self.space).__name__}_{hash(self.space)}_param__"

    @property
    @override
    def annotation(self) -> str:
        param = self.get_param(self.value_param)
        options = self._format_param_options(param)
        description = param.description
        return "".join(
            (
                f"  - {param.name}: A {self.value_accepted_type.__name__} "
                "controlling the importance of this space compared to others.",
                f"\n    - **Possible values:** {options}." if options else "",
                f"\n    - **Description:** {description}" if description else "",
                "\n    - **Usage:** Positive values (e.g., `1.0`) boost matches; ",
                "higher values increase importance. Negative values (e.g., `-1.0`) penalize matches. ",
                "Zero (`0.0`) means no effect.",
            )
        )

    @property
    @override
    def value_accepted_type(self) -> type:
        return float


@dataclass(frozen=True)
class LooksLikeFilterClause(
    WeightedQueryClause[EvaluatedBinaryPredicate[LooksLikePredicate] | None],
    HasAnnotation,
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
        return f"with_vector_{self.schema_field.name}_value_param__"

    @override
    def get_default_weight_param_name(self) -> str:
        return f"with_vector_{self.schema_field.name}_weight_param__"

    @property
    @override
    def annotation(self) -> str:
        value_param = self.get_param(self.value_param)
        weight_param = self.get_param(self.weight_param)
        v_options = self._format_param_options(value_param)
        w_options = self._format_param_options(weight_param)
        v_description = value_param.description or ""
        w_description = weight_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {self.value_accepted_type.__name__} "
                "representing a similarity-search item for each space.",
                f"\n    - **Possible values:** {v_options}." if v_options else "",
                f"\n    - **Description:** {v_description}" if v_description else "",
                "\n    - **Usage:** Retrieves a vector using the identifier, split it "
                "into parts for each space, and treat each part as a similarity-search item.",
                f"\n  - {weight_param.name}: A {self.weight_accepted_type.__name__} controlling "
                "the importance of this similarity-search item within each space.",
                (f"\n    - **Possible values:** {w_options}." if w_options else ""),
                f"\n    - **Description:** {w_description}" if w_description else "",
                "\n    - **Usage:** Same as `space_weight`, but within the space",
            )
        )

    @property
    @override
    def value_accepted_type(self) -> type:
        return str


@dataclass(frozen=True)
class SimilarFilterClause(
    WeightedQueryClause[tuple[Space, Weighted[PythonTypes]] | None],
    HasAnnotation,
):
    field_set: SpaceFieldSet

    @property
    def space(self) -> Space:
        return self.field_set.space

    @override
    def evaluate(
        self,
    ) -> tuple[Space, Weighted[PythonTypes]] | None:
        value = self.get_value()
        weight = self.get_weight()
        if value is None or weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT:
            return None
        return (self.space, Weighted(value, weight))

    @override
    def get_default_value_param_name(self) -> str:
        return f"similar_filter_{self.space}_{self.field_set.fields_id}_value_param__"

    @override
    def get_default_weight_param_name(self) -> str:
        return f"similar_filter_{self.space}_{self.field_set.fields_id}_weight_param__"

    @property
    @override
    def annotation(self) -> str:
        value_param = self.get_param(self.value_param)
        weight_param = self.get_param(self.weight_param)
        v_options = self._format_param_options(value_param)
        w_options = self._format_param_options(weight_param)
        v_description = value_param.description or ""
        w_description = weight_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {self.value_accepted_type.__name__} "
                "representing a similarity-search item.",
                f"\n    - **Possible values:** {v_options}." if v_options else "",
                f"\n    - **Description:** {v_description}" if v_description else "",
                "\n    - **Usage:** Encoded into a vector, used to find similar items, "
                "and combined with others based on weights.",
                f"\n  - {weight_param.name}: A {self.weight_accepted_type.__name__} "
                "controlling the importance of this similarity-search item within the same space.",
                (f"\n    - **Possible values:** {w_options}." if w_options else ""),
                f"\n    - **Description:** {w_description}" if w_description else "",
                "\n    - **Usage:** Same as `space_weight`, but within the space",
            )
        )

    @property
    @override
    def value_accepted_type(self) -> type:
        return self.field_set.input_type

    @override
    def get_allowed_values(self, param: Param | Evaluated[Param]) -> set[ParamInputType]:
        if param == self.weight_param:
            return super().get_allowed_values(self.weight_param)
        categories: set[ParamInputType] = (
            set(self.space._embedding_config.categories)
            if isinstance(self.space, CategoricalSimilaritySpace)
            else set()
        )
        options = self.get_param(param).options or set()
        if options and not categories:
            return options
        if categories and not options:
            return categories
        return options.intersection(categories)


@dataclass(frozen=True)
class HardFilterClause(QueryClause[ComparisonOperation[SchemaField] | None], HasAnnotation):
    op: ComparisonOperationType
    operand: SchemaField
    group_key: int | None

    @override
    def get_default_value_param_name(self) -> str:
        return f"hard_filter_{self.operand.name}_{self.op.value}_param__"

    @override
    def evaluate(self) -> ComparisonOperation[SchemaField] | None:
        value = self.get_value()
        if value is None:
            return None
        operation = ComparisonOperation(self.op, self.operand, value, self.group_key)
        QueryFilterValidator.validate_operation_operand_type(operation, allow_param=False)
        return operation

    @property
    @override
    def annotation(self) -> str:
        value_param = self.get_param(self.value_param)
        options = self._format_param_options(value_param)
        description = value_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {self.value_accepted_type.__name__} "
                f"that must {self.op.value.replace('_', ' ')} the `body` field.",
                f"\n    - **Possible values:** {options}." if options else "",
                f"\n    - **Description:** {description}" if description else "",
            )
        )

    @property
    @override
    def value_accepted_type(self) -> type:
        return GenericClassUtil.get_single_generic_type(self.operand)


@dataclass(frozen=True)
class NLQClause(QueryClause[str | None]):
    client_config: OpenAIClientConfig

    @override
    def get_default_value_param_name(self) -> str:
        return "natural_query_param__"

    @override
    def evaluate(self) -> str | None:
        value = self.get_value()
        if value is not None and not isinstance(value, str):
            raise QueryException(f"NLQ prompt should be str, got {type(value).__name__}.")
        return value


@dataclass(frozen=True)
class NLQSystemPromptClause(QueryClause[str | None]):

    @override
    def get_default_value_param_name(self) -> str:
        return "system_prompt_param__"

    @override
    def evaluate(self) -> str | None:
        value = self.get_value()
        if value is not None and not isinstance(value, str):
            raise QueryException(f"NLQ system prompt should be str, got {type(value).__name__}.")
        return value


@dataclass(frozen=True)
class LimitClause(QueryClause[int]):

    @override
    def get_default_value_param_name(self) -> str:
        return "limit_param__"

    @override
    def get_value(self) -> int:
        if (value := super().get_value()) is not None:
            if not isinstance(value, int):
                raise QueryException(f"Limit should be int, got {type(value).__name__}.")
            return value
        return constants.DEFAULT_LIMIT

    @override
    def evaluate(self) -> int:
        return self.get_value()


@dataclass(frozen=True)
class SelectClause(QueryClause[list[str]]):
    @override
    def get_default_value_param_name(self) -> str:
        return "select_param__"

    @override
    def get_value(self) -> list[str]:
        value = super().get_value()
        if value is None:
            return []
        TypeValidator.validate_list_item_type(value, str, "Query select clause value")
        return cast(list[str], value)

    @override
    def evaluate(self) -> list[str]:
        return self.get_value()

    @override
    def _transform_param_value(self, param_value: Any) -> Any:
        if TypeValidator.is_sequence_safe(param_value):
            return [value.name if isinstance(value, SchemaField) else value for value in param_value]
        return param_value


@dataclass(frozen=True)
class RadiusClause(QueryClause[float | None]):
    @override
    def get_default_value_param_name(self) -> str:
        return "radius_param__"

    @override
    def get_value(self) -> float | None:
        if (value := super().get_value()) is not None:
            if not isinstance(value, int | float):
                raise QueryException(f"Radius should be numeric, got {type(value).__name__}.")
            return float(value)
        return None

    @override
    def evaluate(self) -> float | None:
        return self.get_value()


@dataclass(frozen=True)
class OverriddenNowClause(QueryClause[int | None]):

    @override
    def get_default_value_param_name(self) -> str:
        return "overridden_now_param__"

    @override
    def evaluate(self) -> int | None:
        if (value := self.get_value()) is not None:
            if not isinstance(value, int):
                raise QueryException(f"'now' should be int, got {type(value).__name__}.")
            return value
        return None
