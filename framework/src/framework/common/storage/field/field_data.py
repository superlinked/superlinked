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

from beartype.typing import Any, Generic, TypeVar, get_args

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.field_type_converter import (
    VALID_TYPE_BY_FIELD_DATA_TYPE,
    FieldTypeConverter,
)

# FieldType
FT = TypeVar("FT")


class FieldData(Field, Generic[FT]):
    def __init__(self, type_: FieldDataType, name: str, value: FT) -> None:
        super().__init__(type_, name)
        self.__validate_value(type_, value)
        self.value = value

    @classmethod
    def from_field(cls, field: Field, value: FT) -> FieldData:
        return cls(field.data_type, field.name, value)

    def __validate_value(self, data_type: FieldDataType, value: FT) -> None:
        valid_types = FieldTypeConverter.get_valid_node_data_types(data_type)
        if not isinstance(value, tuple(valid_types)):
            self.__raise_validation_exception(data_type, value)
        self.__validate_list_type(data_type, value)

    def __validate_list_type(self, data_type: FieldDataType, value: FT) -> None:
        if not isinstance(value, list):
            return
        if data_type == FieldDataType.FLOAT_LIST:
            if self.__is_valid_float_list(value):
                return
            self.__raise_validation_exception(data_type, value)
        valid_type = VALID_TYPE_BY_FIELD_DATA_TYPE[data_type][0]
        generic_type = get_args(valid_type)[0]
        if not all(isinstance(item, generic_type) for item in value):
            self.__raise_validation_exception(data_type, value)

    def __is_valid_float_list(self, value: list[Any]) -> bool:
        """
        This is a performance hot-spot. It needs to be fast as we use it
        for custom space input validation where we can have long float lists
        """
        try:
            for item in value:
                float(item)
            return True
        except (ValueError, TypeError):
            return False

    def __raise_validation_exception(self, data_type: FieldDataType, value: Any) -> None:
        raise InvalidInputException(f"Invalid value {value} for the given field data type {data_type}")


class VectorFieldData(FieldData[Vector]):
    def __init__(self, name: str, value: Vector) -> None:
        super().__init__(FieldDataType.VECTOR, name, value)
