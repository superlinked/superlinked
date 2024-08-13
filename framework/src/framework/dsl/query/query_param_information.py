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

from dataclasses import dataclass, field
from enum import Enum

from beartype.typing import Any, cast

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.lazy_property import lazy_property
from superlinked.framework.dsl.query.param import Param, ParamInputType, ParamType
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["ParamInfo"] = False
__pdoc__["ParamGroup"] = False
__pdoc__["WeightedParamInfo"] = False
__pdoc__["QueryParamInformation"] = False


class ParamGroup(Enum):
    SPACE_WEIGHT = "space_weight_param"
    HARD_FILTER = "hard_filter_param"
    SIMILAR_FILTER_VALUE = "similar_filter_value_param"
    SIMILAR_FILTER_WEIGHT = "similar_filter_weight_param"
    LOOKS_LIKE_FILTER_VALUE = "looks_like_filter_value_param"
    LOOKS_LIKE_FILTER_WEIGHT = "looks_like_filter_weight_param"
    LIMIT = "limit_param"
    RADIUS = "radius_param"
    NATURAL_QUERY = "natural_query_param"


@dataclass(frozen=True)
class WeightedParamInfo:
    value_param: ParamInfo
    weight_param: ParamInfo

    @classmethod
    def init_with(  # pylint: disable=too-many-arguments
        cls,
        value_param_group: ParamGroup,
        weight_param_group: ParamGroup,
        value_param: ParamType,
        weight_param: ParamType,
        schema_field: SchemaField | None = None,
        space: Space | None = None,
    ) -> WeightedParamInfo:
        return cls(
            ParamInfo.init_with(value_param_group, value_param, schema_field, space),
            ParamInfo.init_with(weight_param_group, weight_param, schema_field, space),
        )


@dataclass(frozen=True)
class ParamInfo:
    name: str
    description: str | None
    value: ParamInputType
    is_weight: bool
    schema_field: SchemaField | None = None
    space: Space | None = None
    op: ComparisonOperationType | None = None

    def copy_with_new_value(self, value: ParamInputType) -> ParamInfo:
        return ParamInfo(
            self.name,
            self.description,
            value,
            self.is_weight,
            self.schema_field,
            self.space,
            self.op,
        )

    @classmethod
    def init_with(
        cls,
        param_group: ParamGroup,
        param: ParamType,
        schema_field: SchemaField | None = None,
        space: Space | None = None,
        op: ComparisonOperationType | None = None,
    ) -> ParamInfo:
        schema_field_name = schema_field.name if schema_field else None
        is_weight = param_group in [
            ParamGroup.SPACE_WEIGHT,
            ParamGroup.SIMILAR_FILTER_WEIGHT,
            ParamGroup.LOOKS_LIKE_FILTER_WEIGHT,
        ]
        if isinstance(param, Param):
            name, description, value = (param.name, param.description, None)
        else:
            default_name = cls._get_default_name(
                param_group,
                is_weight,
                space,
                schema_field_name,
                op,
            )
            name, description, value = (default_name, None, cast(ParamInputType, param))
        return cls(name, description, value, is_weight, schema_field, space, op)

    @classmethod
    def _get_default_name(
        cls,
        param_group: ParamGroup,
        is_weight: bool,
        space: Space | None,
        schema_field_name: str | None,
        op: ComparisonOperationType | None,
    ) -> str:
        parts = [
            type(space).__name__ if space else None,
            str(hash(space)) if space else None,
            schema_field_name,
            param_group.value,
            op.value if op else None,
            "weight" if is_weight else "value",
        ]
        return "_".join(part for part in parts if part is not None)


@dataclass(frozen=True)
class QueryParamInformation:
    space_weight_params: list[ParamInfo] = field(default_factory=list)
    hard_filter_params: list[ParamInfo] = field(default_factory=list)
    similar_filter_params: list[WeightedParamInfo] = field(default_factory=list)
    looks_like_filter_param: WeightedParamInfo | None = None
    limit_param: ParamInfo | None = None
    radius_param: ParamInfo | None = None
    natural_query_param: ParamInfo | None = None

    def alter(  # pylint: disable=too-many-arguments
        self,
        space_weight_params: list[ParamInfo] | None = None,
        hard_filter_params: list[ParamInfo] | None = None,
        similar_filter_params: list[WeightedParamInfo] | None = None,
        looks_like_filter_param: WeightedParamInfo | None = None,
        limit_param: ParamInfo | None = None,
        radius_param: ParamInfo | None = None,
        natural_query_param: ParamInfo | None = None,
    ) -> QueryParamInformation:
        return QueryParamInformation(
            space_weight_params or self.space_weight_params,
            hard_filter_params or self.hard_filter_params,
            similar_filter_params or self.similar_filter_params,
            looks_like_filter_param or self.looks_like_filter_param,
            limit_param or self.limit_param,
            radius_param or self.radius_param,
            natural_query_param or self.natural_query_param,
        )

    def alter_with_values(
        self,
        new_value_by_name: dict[str, Any],
        override_already_set: bool,
    ) -> QueryParamInformation:
        def update(param: ParamInfo) -> ParamInfo:
            return self._copy_param_with_new_value(
                param, new_value_by_name, override_already_set
            )

        def update_w(
            weighted_param: WeightedParamInfo,
        ) -> WeightedParamInfo:
            return WeightedParamInfo(
                update(weighted_param.value_param),
                update(weighted_param.weight_param),
            )

        looks_like_param = self.looks_like_filter_param
        nlq_param = self.natural_query_param
        return QueryParamInformation(
            [update(param) for param in self.space_weight_params],
            [update(param) for param in self.hard_filter_params],
            [update_w(weighted_param) for weighted_param in self.similar_filter_params],
            update_w(looks_like_param) if looks_like_param else looks_like_param,
            update(self.limit_param) if self.limit_param else self.limit_param,
            update(self.radius_param) if self.radius_param else self.radius_param,
            update(nlq_param) if nlq_param else nlq_param,
        )

    @classmethod
    def _copy_param_with_new_value(
        cls,
        param_info: ParamInfo,
        new_value_by_name: dict[str, Any],
        override_already_set: bool,
    ) -> ParamInfo:
        new_value = new_value_by_name.get(param_info.name)
        can_be_overridden = param_info.value is None or override_already_set
        value = (
            new_value
            if new_value is not None and can_be_overridden
            else param_info.value
        )
        return param_info.copy_with_new_value(value)

    @lazy_property
    def natural_query(self) -> str | None:
        if not self.natural_query_param or self.natural_query_param.value is None:
            return None
        value = self.natural_query_param.value
        if not isinstance(value, str):
            raise QueryException(
                f"Natural query should be string, got {type(value).__name__}"
            )
        return value

    @lazy_property
    def space_weight_map(self) -> dict[Space, float]:
        space_weight_map = {}
        for param in self.space_weight_params:
            value = (
                constants.DEFAULT_NOT_AFFECTING_WEIGHT
                if param.value is None
                else param.value
            )
            if not isinstance(value, (int, float)):
                raise QueryException(
                    f"Space weight should be numeric, got {type(value).__name__}."
                )
            if not isinstance(param.space, Space):
                raise QueryException(
                    f"Space weight space should be Space, got {type(param.space).__name__}."
                )
            if param.space in space_weight_map:
                raise QueryException(
                    f"Multiple weights set to {type(param.space).__name__}."
                )
            space_weight_map[param.space] = float(value)
        return space_weight_map

    @lazy_property
    def limit(self) -> int:
        value = self.limit_param.value if self.limit_param else None
        if value is None:
            return constants.DEFAULT_LIMIT
        if not isinstance(value, int):
            raise QueryException(f"Limit should be int, got {type(value).__name__}")
        return value

    @lazy_property
    def radius(self) -> float | None:
        value = self.radius_param.value if self.radius_param else None
        if value is None:
            return None
        if not isinstance(value, (float, int)):
            raise QueryException(
                f"Radius should be numeric, got {type(value).__name__}"
            )
        if value > constants.RADIUS_MAX or value < constants.RADIUS_MIN:
            raise ValueError(
                f"Not a valid Radius value ({value}). It should be between "
                f"{constants.RADIUS_MAX} and {constants.RADIUS_MIN}."
            )
        return float(value)

    @lazy_property
    def nlq_param_infos(self) -> list[ParamInfo]:
        similar_filter_params = self.similar_filter_params
        looks_like = self.looks_like_filter_param
        nested_params = [
            self.space_weight_params,
            self.hard_filter_params,
            [weighted.value_param for weighted in similar_filter_params],
            [weighted.weight_param for weighted in similar_filter_params],
            [looks_like.value_param, looks_like.weight_param] if looks_like else [],
        ]
        return [param for param_list in nested_params for param in param_list]

    @lazy_property
    def knn_params(self) -> dict[str, Any]:
        similar_filter_params = self.similar_filter_params
        looks_like = self.looks_like_filter_param
        return {
            param.name: param.value
            for param_list in [
                self.space_weight_params,
                self.hard_filter_params,
                [weighted.value_param for weighted in similar_filter_params],
                [weighted.weight_param for weighted in similar_filter_params],
                [looks_like.value_param, looks_like.weight_param] if looks_like else [],
                [looks_like.value_param, looks_like.weight_param] if looks_like else [],
                [self.limit_param] if self.limit_param else [],
                [self.radius_param] if self.radius_param else [],
                [self.natural_query_param] if self.natural_query_param else [],
            ]
            for param in param_list
        }
