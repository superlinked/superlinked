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

from dataclasses import dataclass
from itertools import chain

from beartype.typing import Any, Generic, cast
from pydantic import BaseModel, Field, create_model

from superlinked.framework.common.const import DEFAULT_NOT_AFFECTING_WEIGHT
from superlinked.framework.common.exception import NotImplementedException
from superlinked.framework.common.interface.comparison_operand import ComparisonOperand
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.dsl.query.param import PIT, ParamInputType
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["EvaluatedParam"] = False
__pdoc__["WeightedEvaluatedParam"] = False
__pdoc__["PydanticFieldInfo"] = False
__pdoc__["NaturalLanguageQueryParams"] = False
__pdoc__["NaturalLanguageQueryParamHandler"] = False

QUERY_MODEL_NAME = "QueryModel"


@dataclass
class EvaluatedParam(Generic[PIT]):
    param_name: str
    description: str | None
    value: PIT


@dataclass
class WeightedEvaluatedParam:
    value: EvaluatedParam[ParamInputType]
    weight: EvaluatedParam[float | None]


@dataclass
class PydanticFieldInfo:
    field: Any
    type_: type
    name: str


@dataclass
class NaturalLanguageQueryParams:
    weight_param_by_space: dict[Space, EvaluatedParam[float | None]]
    hard_filter_param_by_schema_field: dict[
        ComparisonOperand[SchemaField], EvaluatedParam[ParamInputType]
    ]
    similar_filter_by_space_by_schema_field: dict[
        SchemaField, dict[Space, WeightedEvaluatedParam]
    ]
    looks_like_filter_param: WeightedEvaluatedParam | None


class NaturalLanguageQueryParamHandler:

    def __init__(self, evaluated_query_params: NaturalLanguageQueryParams) -> None:
        self.params = evaluated_query_params

    def to_pydantic(self) -> type[BaseModel]:
        space_weight_fields = [
            self._calculate_pydantic_field_info(weight_param, True, space)
            for space, weight_param in self.params.weight_param_by_space.items()
        ]
        hard_filter_fields = [
            self._calculate_pydantic_field_info(
                weight_param, False, None, cast(SchemaField, schema_field)
            )
            for schema_field, weight_param in self.params.hard_filter_param_by_schema_field.items()
        ]
        similar_fields = [
            self._calculate_weighted_pydantic_fields(
                similar_filter, space, schema_field
            )
            for schema_field, similar_filter_by_space in self.params.similar_filter_by_space_by_schema_field.items()
            for space, similar_filter in similar_filter_by_space.items()
        ]
        looks_like_fields: list[PydanticFieldInfo] = (
            self._calculate_weighted_pydantic_fields(
                self.params.looks_like_filter_param, None, None, str
            )
        )
        all_fields: list[PydanticFieldInfo] = (
            space_weight_fields
            + hard_filter_fields
            + list(chain.from_iterable(similar_fields))
            + looks_like_fields
        )
        typed_fields_by_name: dict[str, Any] = {
            field_info.name: (field_info.type_, field_info.field)
            for field_info in all_fields
        }
        model_cls = create_model(QUERY_MODEL_NAME, **typed_fields_by_name)
        return model_cls

    def _calculate_weighted_pydantic_fields(
        self,
        weighted_param: WeightedEvaluatedParam | None,
        space: Space | None = None,
        schema_field: SchemaField | None = None,
        type_: type | None = None,
    ) -> list[PydanticFieldInfo]:
        if not weighted_param:
            return []
        value_field = self._calculate_pydantic_field_info(
            weighted_param.value, False, space, schema_field, type_
        )
        weight_field = self._calculate_pydantic_field_info(
            weighted_param.weight, True, space
        )
        return [value_field, weight_field]

    def _calculate_pydantic_field_info(
        self,
        evaluated_param: EvaluatedParam,
        is_weight: bool = True,
        space: Space | None = None,
        schema_field: SchemaField | None = None,
        type_: type | None = None,
    ) -> PydanticFieldInfo:
        is_unset_weight = is_weight and evaluated_param.value is None
        value = (
            DEFAULT_NOT_AFFECTING_WEIGHT if is_unset_weight else evaluated_param.value
        )
        name = evaluated_param.param_name
        field = Field(
            default=value,
            description=evaluated_param.description,
            json_schema_extra={
                "is_unset_weight": is_unset_weight,
                "space": space.__class__.__name__ if space else None,
                "schema_field": schema_field.name if schema_field else None,
            },
        )
        type_ = self._determine_type(type_, is_weight, schema_field, value)
        return PydanticFieldInfo(field, type_, name)

    def _determine_type(
        self,
        type_: type | None,
        is_weight: bool,
        schema_field: SchemaField | None,
        value: Any,
    ) -> type:
        if type_ is not None:
            return type_
        if is_weight:
            return float
        if schema_field:
            return GenericClassUtil.get_single_generic_type(schema_field)
        if value:
            return type(value)
        # should not be raised
        raise NotImplementedException("Type could not be identified")
