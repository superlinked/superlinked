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

from dataclasses import dataclass, field, replace

from beartype.typing import Any, Mapping, Sequence, cast
from typing_extensions import Self, override

from superlinked.framework.common.const import constants
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.dsl.query.nlq.param_filler.nlq_annotation import (
    NLQAnnotation,
)
from superlinked.framework.dsl.query.param import (
    NumericParamType,
    ParamInputType,
    StringParamType,
)
from superlinked.framework.dsl.query.query_clause.base_looks_like_filter_clause import (
    BaseLooksLikeFilterClause,
)
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.query_clause.space_weight_map import SpaceWeightMap
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.space import Space

SPACE_WEIGHT_MAP_ATTRIBUTE = "space_weight_map"
DEFAULT_PARAM_NAME_PREFIX = "with_vector"


@dataclass(frozen=True)
class LooksLikeFilterClauseWeightBySpace(BaseLooksLikeFilterClause):
    space_weight_map: SpaceWeightMap = field(default_factory=SpaceWeightMap)

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return [*super().params, *self.space_weight_map.params]

    @property
    @override
    def nlq_annotations(self) -> list[NLQAnnotation]:
        # NLQ does not support weight dict.
        return []

    @override
    def get_weight_param_name_by_space(self) -> dict[Space | None, str]:
        base = super().get_weight_param_name_by_space()
        return base | {
            space: QueryClause.get_param(weight_param).name for space, weight_param in self.space_weight_map.items()
        }

    @override
    def get_default_value_by_param_name(self) -> dict[str, Any]:
        defaults = super().get_default_value_by_param_name()
        missing_weight_params = {
            QueryClause.get_param(weight).name: BaseLooksLikeFilterClause._get_default_weight(weight)
            for weight in self.space_weight_map.values()
        }
        return defaults | missing_weight_params

    @override
    def set_defaults_for_nlq(self) -> Self:
        clause = super().set_defaults_for_nlq()
        evaluated_weight_params = {
            QueryClause.get_param(weight_param).name: constants.DEFAULT_WEIGHT
            for weight_param in clause.space_weight_map.values()  # pylint: disable=no-member
            if not isinstance(weight_param, Evaluated)
        }
        altered_space_map = clause.space_weight_map.alter_param_values(  # pylint: disable=no-member
            evaluated_weight_params, False
        )
        if not altered_space_map:
            return clause
        changes: dict[str, Any] = {SPACE_WEIGHT_MAP_ATTRIBUTE: altered_space_map}
        return replace(clause, **changes)

    @override
    def _evaluate_changes(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> dict[str, Evaluated[TypedParam]]:
        changes = super()._evaluate_changes(param_values, is_override_set)
        weight_param_changes = self.space_weight_map.alter_param_values(param_values, is_override_set)
        return changes | {SPACE_WEIGHT_MAP_ATTRIBUTE: weight_param_changes} if weight_param_changes else changes

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        self.space_weight_map.set_param_name_if_unset(f"{DEFAULT_PARAM_NAME_PREFIX}_{self.schema_field.name}")

    @override
    def _get_weight(self) -> float | dict[str, float]:
        def calculate_weight(weight_param: TypedParam | Evaluated[TypedParam]) -> float:
            value = cast(float | None, QueryClause._get_param_value(weight_param))
            return float(value) if value is not None else constants.DEFAULT_WEIGHT

        weight_by_node_id = {
            space._get_embedding_node(self.schema_field.schema_obj).node_id: calculate_weight(weight_param)
            for space, weight_param in self.space_weight_map.items()
        }
        return weight_by_node_id

    @classmethod
    def from_param(
        cls, id_: IdField, id_param: StringParamType, weight: Mapping[Space, NumericParamType]
    ) -> LooksLikeFilterClauseWeightBySpace:
        value_param = QueryClause._to_typed_param(id_param, [str])
        weight_param = {
            space: QueryClause._to_typed_param(weight_param, [float]) for space, weight_param in weight.items()
        }
        return LooksLikeFilterClauseWeightBySpace(value_param, id_, SpaceWeightMap(weight_param))
