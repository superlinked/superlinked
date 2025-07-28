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

from dataclasses import dataclass, field, replace

from beartype.typing import Any, Iterator, Mapping, Sequence
from typing_extensions import Self, override

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.dsl.query.param import (
    UNSET_PARAM_NAME,
    NumericParamType,
    Param,
    ParamInputType,
)
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.space import Space

SPACE_WEIGHTS_ATTRIBUTE = "space_weights"


@dataclass(frozen=True)
class SpaceWeightMap(Mapping[Space, TypedParam | Evaluated[TypedParam]]):
    space_weights: Mapping[Space, TypedParam | Evaluated[TypedParam]] = field(default_factory=dict)

    @property
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return list(self.values())

    def set_param_name_if_unset(self, prefix: str) -> None:
        def get_default_weight_param_name(space: Space) -> str:
            return f"{prefix}_{space}_param__"

        for space, weight_param in self.items():
            param = QueryClause.get_param(weight_param)
            if param.name is UNSET_PARAM_NAME:
                param.name = get_default_weight_param_name(space)

    def alter_param_values(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> Self | None:
        if not param_values:
            return None
        weight_param_changes: dict[str, Any] | None = self.__get_weight_param_changes(
            self, param_values, is_override_set
        )
        if weight_param_changes is None:
            return None
        return replace(self, **weight_param_changes)  # pylint: disable=not-a-mapping # it is a mapping

    def extend(
        self,
        weight_param_by_space: Mapping[Space, NumericParamType],
        all_space: Sequence[Space],
    ) -> Self:
        if not weight_param_by_space:
            return self
        self.__validate_params(weight_param_by_space, all_space)
        changes = {
            SPACE_WEIGHTS_ATTRIBUTE: dict(self)
            | {
                space: QueryClause._to_typed_param(weight_param, [float])
                for space, weight_param in weight_param_by_space.items()
            }
        }
        return replace(self, **changes)

    @override
    def __getitem__(self, key: Space) -> TypedParam | Evaluated[TypedParam]:
        return self.space_weights[key]

    @override
    def __iter__(self) -> Iterator[Space]:
        return iter(self.space_weights)

    @override
    def __len__(self) -> int:
        return len(self.space_weights)

    def __get_weight_param_changes(
        self,
        weight_param_by_space: Mapping[Space, TypedParam | Evaluated[TypedParam]],
        param_values: Mapping[str, ParamInputType | None],
        is_override_set: bool,
    ) -> dict[str, dict[Space, TypedParam | Evaluated[TypedParam]]] | None:
        subchanges = dict[Space, TypedParam | Evaluated[TypedParam]]()
        for space, weight_param in weight_param_by_space.items():
            if modified_param := QueryClause._get_single_param_modification(
                weight_param, param_values, is_override_set
            ):
                subchanges[space] = modified_param
        return {SPACE_WEIGHTS_ATTRIBUTE: dict(weight_param_by_space) | subchanges} if subchanges else None

    def __validate_params(
        self,
        weight_param_by_space: Mapping[Space, NumericParamType],
        all_space: Sequence[Space],
    ) -> None:
        if bound_spaces := set(self.keys()).intersection(weight_param_by_space.keys()):
            bound_space_names = ",".join([type(space).__name__ for space in bound_spaces])
            raise InvalidInputException(
                f"Attempted to bound space weight(s) for {bound_space_names} space(s) in Query multiple times."
            )
        in_use_param_names = [QueryClause.get_param(weight).name for weight in self.values()]
        if weight_param_names := [
            weight_param.name
            for weight_param in weight_param_by_space.values()
            if isinstance(weight_param, Param) and weight_param.name in in_use_param_names
        ]:
            raise InvalidInputException(
                f"Attempted to bound space weight with parameter name(s) {weight_param_names} already in use."
            )
        for space in weight_param_by_space.keys():
            if space not in all_space:
                raise InvalidInputException(f"Space isn't present in the index: {type(space).__name__}.")
