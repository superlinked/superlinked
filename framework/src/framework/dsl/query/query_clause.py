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
    ITERABLE_COMPARISON_OPERATION_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.interface.has_annotation import HasAnnotation
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.dsl.query.param import (
    UNSET_PARAM_NAME,
    IntParamType,
    NumericParamType,
    Param,
    ParamInputType,
    ParamType,
    StringParamType,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

EvaluatedQueryT = TypeVar("EvaluatedQueryT")

VALUE_PARAM_FIELD = "value_param"
WEIGHT_PARAM_FIELD = "weight_param"


@dataclass(frozen=True)
class QueryClause(Generic[EvaluatedQueryT]):
    value_param: TypedParam | Evaluated[TypedParam]

    def __post_init__(self) -> None:
        self._set_param_name_if_unset()

    @abstractmethod
    def evaluate(self) -> EvaluatedQueryT: ...

    @abstractmethod
    def get_default_value_param_name(self) -> str: ...

    @property
    def _value_accepted_type(self) -> type:
        raise RuntimeError("This method should not be used.")

    @property
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return [self.value_param]

    @property
    def value_param_name(self) -> str:
        return QueryClause.get_param(self.value_param).name

    @property
    def is_type_mandatory_in_nlq(self) -> bool:
        return True

    def get_value(self) -> PythonTypes | None:
        value = QueryClause.get_param_value(self.value_param)
        return cast(PythonTypes | None, value)

    def get_param_value_by_param_name(self) -> dict[str, PythonTypes | None]:
        return {self.value_param_name: self.get_value()}

    def get_param_name_by_space(self) -> dict[Space, str]:
        return dict[Space, str]()

    def alter_param_values(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> Self:
        changes = self._evaluate_changes(params_values, is_override_set)
        return replace(self, **changes) if changes else self

    def set_defaults_for_nlq(self) -> Self:
        return self

    def get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) -> set[ParamInputType]:
        return QueryClause.get_param(param).options

    def _evaluate_changes(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> dict[str, Any]:
        if modified_param := self._get_single_param_modification(self.value_param, params_values, is_override_set):
            return {VALUE_PARAM_FIELD: modified_param}
        return {}

    def _get_single_param_modification(
        self,
        param: TypedParam | Evaluated[TypedParam],
        params_values: Mapping[str, ParamInputType],
        is_override_set: bool,
    ) -> Evaluated[TypedParam] | None:
        param_to_alter = QueryClause.get_typed_param(param)
        if (is_override_set or not isinstance(param, Evaluated)) and (
            value := params_values.get(param_to_alter.param.name)
        ) is not None:
            return param_to_alter.evaluate(value)
        return None

    def _set_param_name_if_unset(self) -> None:
        if self.value_param_name is UNSET_PARAM_NAME:
            QueryClause.get_param(self.value_param).name = self.get_default_value_param_name()

    @staticmethod
    def get_typed_param(typed_param: TypedParam | Evaluated[TypedParam]) -> TypedParam:
        return typed_param.item if isinstance(typed_param, Evaluated) else typed_param

    @staticmethod
    def get_param(typed_param: TypedParam | Evaluated[TypedParam]) -> Param:
        return QueryClause.get_typed_param(typed_param).param

    @staticmethod
    def get_param_value(param: TypedParam | Evaluated[TypedParam]) -> ParamInputType | None:
        default = QueryClause.get_param(param).default
        if isinstance(param, Evaluated):
            if param.value is None:
                return default
            return param.value
        return default

    @staticmethod
    def get_value_by_param_name(param: TypedParam | Evaluated[TypedParam]) -> dict[str, ParamInputType | None]:
        return {QueryClause.get_param(param).name: QueryClause.get_param_value(param)}

    @staticmethod
    def _format_param_options(param: Param) -> str:
        return ", ".join(sorted(str(value) for value in param.options))

    @staticmethod
    def _to_typed_param(
        param_input: Any,
        param_types: Sequence[type],
    ) -> TypedParam | Evaluated[TypedParam]:
        param_input = cast(ParamInputType, param_input)
        if isinstance(param_input, Param):
            return TypedParam.from_unchecked_types(param_input, param_types)
        return TypedParam.init_evaluated(param_types, param_input)


QueryClauseT = TypeVar("QueryClauseT", bound=QueryClause)


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
        param = QueryClause.get_param(self.value_param)
        options = QueryClause._format_param_options(param)
        description = param.description
        return "".join(
            (
                f"  - {param.name}: A {self._value_accepted_type.__name__} "
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
    def _value_accepted_type(self) -> type:
        return float

    @classmethod
    def from_param(cls, weight: NumericParamType, space: Space) -> SpaceWeightClause:
        return SpaceWeightClause(QueryClause._to_typed_param(weight, [float]), space)


@dataclass(frozen=True)
class LooksLikeFilterClause(
    QueryClause[tuple[str, float | dict[str, float]] | None],
    HasAnnotation,
):
    schema_field: SchemaField
    weight_param: TypedParam | Evaluated[TypedParam] | dict[Space, TypedParam | Evaluated[TypedParam]]

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        weight_params = list(self.weight_param.values()) if isinstance(self.weight_param, dict) else [self.weight_param]
        return [*super().params, *weight_params]

    @property
    def weight_param_names(self) -> list[str]:
        if isinstance(self.weight_param, dict):
            return [QueryClause.get_param(weight_param).name for weight_param in self.weight_param.values()]
        return [QueryClause.get_param(self.weight_param).name]

    @override
    def _evaluate_changes(
        self, params_values: Mapping[str, ParamInputType], is_override_set: bool
    ) -> dict[str, Evaluated[TypedParam]]:
        changes = super()._evaluate_changes(params_values, is_override_set)
        weight_param_changes: dict[str, Any] | None
        if isinstance(self.weight_param, dict):
            weight_param_changes = self.__get_dict_weight_param_related_changes(
                self.weight_param, params_values, is_override_set
            )
        else:
            weight_param_changes = self.__get_weight_param_related_changes(
                self.weight_param, params_values, is_override_set
            )
        return changes | weight_param_changes if weight_param_changes else changes

    def __get_weight_param_related_changes(
        self,
        weight_param: TypedParam | Evaluated[TypedParam],
        params_values: Mapping[str, ParamInputType],
        is_override_set: bool,
    ) -> dict[str, TypedParam | Evaluated[TypedParam]] | None:
        modified_param = self._get_single_param_modification(weight_param, params_values, is_override_set)
        return {WEIGHT_PARAM_FIELD: modified_param} if modified_param else None

    def __get_dict_weight_param_related_changes(
        self,
        weight_params: dict[Space, TypedParam | Evaluated[TypedParam]],
        params_values: Mapping[str, ParamInputType],
        is_override_set: bool,
    ) -> dict[str, dict[Space, TypedParam | Evaluated[TypedParam]]] | None:
        subchanges = dict[Space, TypedParam | Evaluated[TypedParam]]()
        for space, weight_param in weight_params.items():
            if modified_param := self._get_single_param_modification(weight_param, params_values, is_override_set):
                subchanges[space] = modified_param
        return {WEIGHT_PARAM_FIELD: weight_params | subchanges} if subchanges else None

    @override
    def get_param_value_by_param_name(self) -> dict[str, PythonTypes | None]:
        base = super().get_param_value_by_param_name()
        if isinstance(self.weight_param, dict):
            weight_param_by_name = {
                key: value
                for weight_param in self.weight_param.values()
                for key, value in QueryClause.get_value_by_param_name(weight_param).items()
            }
        else:
            weight_param_by_name = QueryClause.get_value_by_param_name(self.weight_param)
        return base | cast(dict[str, PythonTypes | None], weight_param_by_name)

    @override
    def evaluate(self) -> tuple[str, float | dict[str, float]] | None:
        def is_weight_unaffecting(weight: float | dict[str, float]) -> bool:
            if isinstance(weight, float):
                return weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT
            return all(space_weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT for space_weight in weight.values())

        value = self.get_value()
        weight = self.__get_weight()
        if value is None or weight is None or is_weight_unaffecting(weight):
            return None
        return cast(str, value), weight

    @override
    def set_defaults_for_nlq(self) -> Self:
        clause = super().set_defaults_for_nlq()
        if not isinstance(self.weight_param, dict):
            return clause
        evaluated_weight_params: dict[Space, TypedParam | Evaluated[TypedParam]] = {
            space: weight_param.evaluate(constants.DEFAULT_WEIGHT)
            for space, weight_param in self.weight_param.items()
            if not isinstance(weight_param, Evaluated)
        }
        if evaluated_weight_params:
            return replace(clause, weight_param=self.weight_param | evaluated_weight_params)
        return clause

    def __get_weight(self) -> float | dict[str, float] | None:
        if isinstance(self.weight_param, dict):
            weight_by_node_id = {
                space._get_embedding_node(self.schema_field.schema_obj).node_id: (
                    weight_param.value if isinstance(weight_param, Evaluated) else constants.DEFAULT_WEIGHT
                )
                for space, weight_param in self.weight_param.items()
            }
            return weight_by_node_id
        if isinstance(self.weight_param, Evaluated):
            return float(self.weight_param.value)
        return constants.DEFAULT_WEIGHT

    @override
    def get_default_value_param_name(self) -> str:
        return f"with_vector_{self.schema_field.name}_value_param__"

    def get_default_weight_param_name(self) -> str:
        return f"with_vector_{self.schema_field.name}_weight_param__"

    @property
    @override
    def _value_accepted_type(self) -> type:
        return str

    @property
    @override
    def annotation(self) -> str:
        if isinstance(self.weight_param, dict):
            # NLQ does not support weight dict.
            return ""
        value_param = QueryClause.get_param(self.value_param)
        weight_param = QueryClause.get_param(self.weight_param)
        v_options = QueryClause._format_param_options(value_param)
        w_options = QueryClause._format_param_options(weight_param)
        v_description = value_param.description or ""
        w_description = weight_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {self._value_accepted_type.__name__} "
                "representing a similarity-search item for each space.",
                f"\n    - **Possible values:** {v_options}." if v_options else "",
                f"\n    - **Description:** {v_description}" if v_description else "",
                "\n    - **Usage:** Retrieves a vector using the identifier, split it "
                "into parts for each space, and treat each part as a similarity-search item.",
                f"\n  - {weight_param.name}: A {float.__name__} controlling "
                "the importance of this similarity-search item within each space.",
                (f"\n    - **Possible values:** {w_options}." if w_options else ""),
                f"\n    - **Description:** {w_description}" if w_description else "",
                "\n    - **Usage:** Same as `space_weight`, but within the space",
            )
        )

    @classmethod
    def from_param(
        cls, id_: IdField, id_param: StringParamType, weight: NumericParamType | Mapping[Space, NumericParamType]
    ) -> LooksLikeFilterClause:
        value_param = QueryClause._to_typed_param(id_param, [str])
        weight_param: TypedParam | Evaluated[TypedParam] | dict[Space, TypedParam | Evaluated[TypedParam]]
        if isinstance(weight, dict):
            weight_param = {
                space: QueryClause._to_typed_param(weight_param, [float]) for space, weight_param in weight.items()
            }
        else:
            weight_param = QueryClause._to_typed_param(weight, [float])
        return LooksLikeFilterClause(value_param, id_, weight_param)


@dataclass(frozen=True)
class SimilarFilterClause(QueryClause[tuple[Space, Weighted[PythonTypes]] | None], HasAnnotation):
    weight_param: TypedParam | Evaluated[TypedParam]
    field_set: SpaceFieldSet

    @property
    def space(self) -> Space:
        return self.field_set.space

    @property
    @override
    def _value_accepted_type(self) -> type:
        return self.field_set.input_type

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return [*super().params, self.weight_param]

    @override
    def get_param_value_by_param_name(self) -> dict[str, PythonTypes | None]:
        return super().get_param_value_by_param_name() | {
            QueryClause.get_param(self.weight_param).name: self._get_weight()
        }

    @override
    def evaluate(
        self,
    ) -> tuple[Space, Weighted[PythonTypes]] | None:
        value = self.get_value()
        weight = self._get_weight()
        if value is None or weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT:
            return None
        return (self.space, Weighted(value, weight))

    @override
    def get_default_value_param_name(self) -> str:
        return f"similar_filter_{self.space}_{self.field_set.fields_id}_value_param__"

    @override
    def get_param_name_by_space(self) -> dict[Space, str]:
        return super().get_param_name_by_space() | {self.space: QueryClause.get_param(self.weight_param).name}

    @override
    def _evaluate_changes(
        self, params_values: Mapping[str, ParamInputType], is_override_set: bool
    ) -> dict[str, Evaluated[TypedParam]]:
        changes = super()._evaluate_changes(params_values, is_override_set)
        if modified_param := self._get_single_param_modification(self.weight_param, params_values, is_override_set):
            return changes | {WEIGHT_PARAM_FIELD: modified_param}
        return changes

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        weight_param = QueryClause.get_param(self.weight_param)
        if weight_param.name is UNSET_PARAM_NAME:
            weight_param.name = self.__get_default_weight_param_name()

    def _get_weight(self) -> float:
        weight = QueryClause.get_param_value(self.weight_param)
        if weight is None:
            weight = constants.DEFAULT_WEIGHT
        if not isinstance(weight, (int, float)):
            raise QueryException(f"Clause weight should be numeric, got {type(weight).__name__}.")
        return float(weight)

    @override
    def get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) -> set[ParamInputType]:
        if param == self.weight_param:
            return super().get_allowed_values(self.weight_param)
        categories: set[ParamInputType] = (
            set(self.space._embedding_config.categories)
            if isinstance(self.space, CategoricalSimilaritySpace)
            else set()
        )
        options = QueryClause.get_param(param).options
        if options and not categories:
            return options
        if categories and not options:
            return categories
        return options.intersection(categories)

    @property
    @override
    def annotation(self) -> str:
        value_param = QueryClause.get_param(self.value_param)
        weight_param = QueryClause.get_param(self.weight_param)
        v_options = QueryClause._format_param_options(value_param)
        w_options = QueryClause._format_param_options(weight_param)
        v_description = value_param.description or ""
        w_description = weight_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {self._value_accepted_type.__name__} "
                "representing a similarity-search item.",
                f"\n    - **Possible values:** {v_options}." if v_options else "",
                f"\n    - **Description:** {v_description}" if v_description else "",
                "\n    - **Usage:** Encoded into a vector, used to find similar items, "
                "and combined with others based on weights.",
                f"\n  - {weight_param.name}: A {float.__name__} "
                "controlling the importance of this similarity-search item within the same space.",
                (f"\n    - **Possible values:** {w_options}." if w_options else ""),
                f"\n    - **Description:** {w_description}" if w_description else "",
                "\n    - **Usage:** Same as `space_weight`, but within the space",
            )
        )

    def __get_default_weight_param_name(self) -> str:
        return f"similar_filter_{self.space}_{self.field_set.fields_id}_weight_param__"

    @classmethod
    def from_param(cls, field_set: SpaceFieldSet, param: ParamType, weight: NumericParamType) -> SimilarFilterClause:
        value_param = QueryClause._to_typed_param(param, field_set.validated_allowed_param_types)
        weight_param = QueryClause._to_typed_param(weight, [float])
        return SimilarFilterClause(value_param, weight_param, field_set)


@dataclass(frozen=True)
class HardFilterClause(QueryClause[ComparisonOperation[SchemaField] | None], HasAnnotation):
    op: ComparisonOperationType
    operand: SchemaField
    group_key: int | None

    @property
    @override
    def is_type_mandatory_in_nlq(self) -> bool:
        return False

    @override
    def get_default_value_param_name(self) -> str:
        return f"hard_filter_{self.operand.name}_{self.op.value}_param__"

    @property
    @override
    def _value_accepted_type(self) -> type:
        return GenericClassUtil.get_single_generic_type(self.operand)

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
        value_param = QueryClause.get_param(self.value_param)
        options = QueryClause._format_param_options(value_param)
        description = value_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {self._value_accepted_type.__name__} "
                f"that must {self.op.value.replace('_', ' ')} the `body` field.",
                f"\n    - **Possible values:** {options}." if options else "",
                f"\n    - **Description:** {description}" if description else "",
            )
        )

    @classmethod
    def from_param(cls, operation: ComparisonOperation[SchemaField]) -> HardFilterClause:
        schema_field = cast(SchemaField, operation._operand)
        param_type: Any = GenericClassUtil.get_single_generic_type(schema_field)
        if operation._op in ITERABLE_COMPARISON_OPERATION_TYPES:
            param_type = list[param_type]
        return HardFilterClause(
            QueryClause._to_typed_param(operation._other, [param_type]),
            operation._op,
            schema_field,
            operation._group_key,
        )


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

    @classmethod
    def from_param(cls, natural_query: StringParamType, client_config: OpenAIClientConfig) -> NLQClause:
        param = QueryClause._to_typed_param(natural_query, [str])
        return NLQClause(param, client_config)


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

    @classmethod
    def from_param(cls, system_prompt: StringParamType) -> NLQSystemPromptClause:
        param = QueryClause._to_typed_param(system_prompt, [str])
        return NLQSystemPromptClause(param)


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

    @classmethod
    def from_param(cls, limit: IntParamType) -> LimitClause:
        return LimitClause(QueryClause._to_typed_param(limit, [int]))


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
        return cast(list[str], value)

    @override
    def evaluate(self) -> list[str]:
        return self.get_value()

    @classmethod
    def from_param(cls, param: Param | Sequence[str]) -> SelectClause:
        return SelectClause(QueryClause._to_typed_param(param, [list[str], list[SchemaField]]))


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

    @classmethod
    def from_param(cls, radius: NumericParamType | None) -> RadiusClause:
        param = (
            QueryClause._to_typed_param(radius, [float])
            if radius is not None
            else TypedParam.init_default([type(None)])
        )
        return RadiusClause(param)


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

    @classmethod
    def from_param(cls, now: IntParamType) -> OverriddenNowClause:
        return OverriddenNowClause(QueryClause._to_typed_param(now, [int]))
