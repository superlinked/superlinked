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
from enum import Enum

from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.param import Param, ParamInputType
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["ParamInfo"] = False
__pdoc__["ParamGroup"] = False
__pdoc__["WeightedParamInfo"] = False


class ParamGroup(Enum):
    SPACE_WEIGHT = "space_weight_param"
    HARD_FILTER = "hard_filter_param"
    SIMILAR_FILTER_VALUE = "similar_filter_value_param"
    SIMILAR_FILTER_WEIGHT = "similar_filter_weight_param"
    LOOKS_LIKE_FILTER_VALUE = "looks_like_filter_value_param"
    LOOKS_LIKE_FILTER_WEIGHT = "looks_like_filter_weight_param"


@dataclass(frozen=True)
class WeightedParamInfo:
    value_param: ParamInfo
    weight_param: ParamInfo

    @classmethod
    def init_with(  # pylint: disable=too-many-arguments
        cls,
        value_param_group: ParamGroup,
        weight_param_group: ParamGroup,
        value_param: Param | Evaluated[Param],
        weight_param: Param | Evaluated[Param],
        schema_field: SchemaField | None = None,
        space: Space | None = None,
    ) -> WeightedParamInfo:
        return cls(
            ParamInfo.init_with(value_param_group, value_param, schema_field, space),
            ParamInfo.init_with(weight_param_group, weight_param, schema_field, space),
        )


@dataclass(frozen=True)
class ParamInfo:  # pylint: disable=too-many-instance-attributes
    name: str
    description: str | None
    value: ParamInputType
    is_weight: bool
    schema_field: SchemaField | None = None
    space: Space | None = None
    op: ComparisonOperationType | None = None
    is_default: bool = False

    def copy_with_new_value(self, value: ParamInputType, is_default: bool) -> ParamInfo:
        return ParamInfo(
            self.name,
            self.description,
            value,
            self.is_weight,
            self.schema_field,
            self.space,
            self.op,
            is_default,
        )

    @classmethod
    def init_with(
        cls,
        param_group: ParamGroup,
        param: Param | Evaluated[Param],
        schema_field: SchemaField | None = None,
        space: Space | None = None,
        op: ComparisonOperationType | None = None,
    ) -> ParamInfo:
        is_weight = param_group in [
            ParamGroup.SPACE_WEIGHT,
            ParamGroup.SIMILAR_FILTER_WEIGHT,
            ParamGroup.LOOKS_LIKE_FILTER_WEIGHT,
        ]
        if isinstance(param, Param):
            name, description, value = (param.name, param.description, param.default)
            is_default = value is not None
        else:
            name, description, value = (
                param.item.name,
                param.item.description,
                param.value,
            )
            is_default = False
        return cls(
            name, description, value, is_weight, schema_field, space, op, is_default
        )
