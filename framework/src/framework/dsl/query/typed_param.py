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

from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.interface.type_converter import (
    IntToFloatConverter,
    TypeConverter,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.type_descriptor import TypeDescriptor, ValidatedValue
from superlinked.framework.dsl.query.param import Param, ParamInputType


class SchemaFieldToStrConverter(TypeConverter[SchemaField, str]):
    def __init__(self) -> None:
        super().__init__(SchemaField, str)

    @override
    def convert(self, base: SchemaField) -> str:
        return base.name


VALID_TYPES_BY_TYPE = {float: (float, int), SchemaField: (str, SchemaField)}
PARAM_TYPE_CONVERTER_BY_TYPE: dict[type, TypeConverter] = {
    float: IntToFloatConverter(),
    SchemaField: SchemaFieldToStrConverter(),
}


@dataclass(frozen=True)
class TypedParam:
    param: Param
    valid_param_value_types: Sequence[TypeDescriptor]

    def __post_init__(self) -> None:
        if self.param.default is not None:
            checked_default = TypedParam.__check_type(self.param.default, self.valid_param_value_types)
            if checked_default != self.param.default:
                raise ValueError(
                    f"Invalid param default: {self.param.default}, needs to be converted to: {checked_default}"
                )

    def __validate_value(self, value: Any) -> Any:
        validated_value = TypedParam.__check_type(value, self.valid_param_value_types)
        self.param._validate_value_allowed(validated_value)
        return validated_value

    def evaluate(self, value: Any) -> Evaluated[TypedParam]:
        value = self.__validate_value(value)
        return Evaluated(self, value)

    @classmethod
    def from_unchecked_types(
        cls,
        param: Param,
        valid_param_value_types: Sequence[type],
    ) -> TypedParam:
        type_descriptors = TypeDescriptor.from_types(
            valid_param_value_types, VALID_TYPES_BY_TYPE, PARAM_TYPE_CONVERTER_BY_TYPE
        )
        if param.default is not None:
            param = Param(
                param.name,
                param.description,
                TypedParam.__check_type(param.default, type_descriptors),
                list(param.options),
            )
        return cls(param, type_descriptors)

    @staticmethod
    def init_evaluated(valid_param_value_types: Sequence[type], value: Any) -> Evaluated[TypedParam]:
        return TypedParam.init_default(valid_param_value_types).evaluate(value)

    @staticmethod
    def init_default(valid_param_value_types: Sequence[type], default: ParamInputType | None = None) -> TypedParam:
        return TypedParam.from_unchecked_types(Param.init_default(default), valid_param_value_types)

    @staticmethod
    def __check_type(value: Any, valid_param_value_types: Sequence[TypeDescriptor]) -> Any:
        original_value = value
        new_value: ValidatedValue | None = next(
            (
                validated_value
                for param_type in valid_param_value_types
                if (validated_value := param_type.validate_value(value)) and validated_value.is_valid
            ),
            None,
        )
        if new_value:
            return new_value.value
        readable_allowed_types = [str(value_type) for value_type in valid_param_value_types]
        raise ValueError(f"Value ({original_value}) is of wrong type. Allowed types are: {readable_allowed_types})")
