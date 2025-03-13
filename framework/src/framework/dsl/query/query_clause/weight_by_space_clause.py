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
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.query.clause_params import QueryVectorClauseParams
from superlinked.framework.dsl.query.param import (
    NumericParamType,
    Param,
    ParamInputType,
)
from superlinked.framework.dsl.query.query_clause.query_clause import (
    NLQCompatible,
    QueryClause,
)
from superlinked.framework.dsl.query.query_clause.space_weight_map import SpaceWeightMap
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.space import Space

SPACE_WEIGHT_MAP_ATTRIBUTE = "space_weight_map"
DEFAULT_PARAM_NAME_PREFIX = "space_weight"


@dataclass(frozen=True)
class WeightBySpaceClause(QueryClause, NLQCompatible):
    space_weight_map: SpaceWeightMap = field(default_factory=SpaceWeightMap)

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return self.space_weight_map.params

    @property
    @override
    def annotation_by_space_annotation(self) -> dict[str, str]:
        return {
            space.annotation: self.__get_annotation(weight_param)
            for space, weight_param in self.space_weight_map.items()
        }

    @override
    def get_altered_query_vector_params(
        self,
        query_vector_params: QueryVectorClauseParams,
        index_node_id: str,
        query_schema: IdSchemaObject,
        storage_manager: StorageManager,
    ) -> QueryVectorClauseParams:
        def get_weight_value(weight_param: TypedParam | Evaluated[TypedParam]) -> float:
            if (value := QueryClause._get_param_value(weight_param)) is not None:
                return cast(float, value)
            return constants.DEFAULT_NOT_AFFECTING_WEIGHT

        alteration = {space: get_weight_value(weight_param) for space, weight_param in self.space_weight_map.items()}
        if not alteration:
            return query_vector_params
        weight_by_space = dict(query_vector_params.weight_by_space)
        return query_vector_params.set_params(weight_by_space=weight_by_space | alteration)

    @override
    def get_space_weight_param_name_by_space(self) -> dict[Space, str]:
        return super().get_space_weight_param_name_by_space() | {
            space: QueryClause.get_param(weight_param).name for space, weight_param in self.space_weight_map.items()
        }

    def extend(self, weight_param_by_space: Mapping[Space, NumericParamType], all_space: Sequence[Space]) -> Self:
        altered_space_weights = self.space_weight_map.extend(weight_param_by_space, all_space)
        if altered_space_weights == self.space_weight_map:
            return self
        return replace(self, **{SPACE_WEIGHT_MAP_ATTRIBUTE: altered_space_weights})

    def add_missing_space_weight_params(self, all_space: Sequence[Space]) -> Self:
        missing_spaces = [space for space in all_space if space not in self.space_weight_map.keys()]
        return self.extend({space: Param.init_default() for space in missing_spaces}, all_space)

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        self.space_weight_map.set_param_name_if_unset(DEFAULT_PARAM_NAME_PREFIX)

    @override
    def _evaluate_changes(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> dict[str, Any]:
        weight_param_changes = self.space_weight_map.alter_param_values(param_values, is_override_set)
        return {SPACE_WEIGHT_MAP_ATTRIBUTE: weight_param_changes} if weight_param_changes else {}

    def __get_annotation(self, weight_param: TypedParam | Evaluated[TypedParam]) -> str:
        param = QueryClause.get_param(weight_param)
        options = QueryClause._format_param_options(param)
        description = param.description
        return "".join(
            (
                f"  - {param.name}: A {float.__name__} " "controlling the importance of this space compared to others.",
                f"\n    - **Possible values:** {options}." if options else "",
                f"\n    - **Description:** {description}" if description else "",
                "\n    - **Usage:** Positive values (e.g., `1.0`) boost matches; ",
                "higher values increase importance. Negative values (e.g., `-1.0`) penalize matches. ",
                "Zero (`0.0`) means no effect.",
            )
        )

    @classmethod
    def from_params(
        cls, weight_param_by_space: Mapping[Space, NumericParamType], all_space: Sequence[Space]
    ) -> WeightBySpaceClause:
        clause = WeightBySpaceClause()
        return clause.extend(weight_param_by_space, all_space)
