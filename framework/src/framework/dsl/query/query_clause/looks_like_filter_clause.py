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

from dataclasses import dataclass

from beartype.typing import Any, Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.dsl.query.nlq.param_filler.nlq_annotation import (
    NLQAnnotation,
    NLQAnnotationType,
)
from superlinked.framework.dsl.query.param import (
    UNSET_PARAM_NAME,
    NumericParamType,
    ParamInputType,
    StringParamType,
)
from superlinked.framework.dsl.query.query_clause.base_looks_like_filter_clause import (
    BaseLooksLikeFilterClause,
)
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.space import Space

WEIGHT_PARAM_FIELD = "weight_param"


@dataclass(frozen=True)
class LooksLikeFilterClause(BaseLooksLikeFilterClause):
    weight_param: TypedParam | Evaluated[TypedParam]

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return [*super().params, self.weight_param]

    @property
    @override
    def nlq_annotations(self) -> list[NLQAnnotation]:
        value_param = QueryClause.get_param(self.value_param)
        weight_param = QueryClause.get_param(self.weight_param)
        v_options = QueryClause._format_param_options(value_param)
        w_options = QueryClause._format_param_options(weight_param)
        v_description = value_param.description or ""
        w_description = weight_param.description or ""
        annotation = "".join(
            (
                f"  - {value_param.name}: A {str.__name__} " "representing a similarity-search item for each space.",
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
        return [NLQAnnotation(annotation, NLQAnnotationType.SPACE_AFFECTING)]

    @override
    def get_weight_param_name_by_space(self) -> dict[Space | None, str]:
        base = super().get_weight_param_name_by_space()
        return base | {None: QueryClause.get_param(self.weight_param).name}

    @override
    def get_default_value_by_param_name(self) -> dict[str, Any]:
        defaults = super().get_default_value_by_param_name()
        missing_weight_params = {
            QueryClause.get_param(self.weight_param).name: BaseLooksLikeFilterClause._get_default_weight(
                self.weight_param
            )
        }
        return defaults | missing_weight_params

    @override
    def _evaluate_changes(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> dict[str, Evaluated[TypedParam]]:
        changes = super()._evaluate_changes(param_values, is_override_set)
        weight_param_changes: dict[str, Any] | None = self.__get_weight_param_changes(
            self.weight_param, param_values, is_override_set
        )
        return changes | weight_param_changes if weight_param_changes else changes

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        param = QueryClause.get_param(self.weight_param)
        if param.name is UNSET_PARAM_NAME:
            param.name = self.__get_default_weight_param_name(space=None)

    @override
    def _get_weight(self) -> float | dict[str, float]:
        if (value := QueryClause._get_param_value(self.weight_param)) is not None:
            return cast(float, value)
        return constants.DEFAULT_WEIGHT

    def __get_weight_param_changes(
        self,
        weight_param: TypedParam | Evaluated[TypedParam],
        param_values: Mapping[str, ParamInputType | None],
        is_override_set: bool,
    ) -> dict[str, TypedParam | Evaluated[TypedParam]] | None:
        modified_param = QueryClause._get_single_param_modification(weight_param, param_values, is_override_set)
        return {WEIGHT_PARAM_FIELD: modified_param} if modified_param else None

    def __get_default_weight_param_name(self, space: Space | None) -> str:
        space_tag = f"{str(space)}_" if space else ""
        return f"with_vector_{self.schema_field.name}_{space_tag}weight_param__"

    @classmethod
    def from_param(cls, id_: IdField, id_param: StringParamType, weight: NumericParamType) -> LooksLikeFilterClause:
        value_param = QueryClause._to_typed_param(id_param, [str])
        weight_param = QueryClause._to_typed_param(weight, [float])
        return LooksLikeFilterClause(value_param, id_, weight_param)
