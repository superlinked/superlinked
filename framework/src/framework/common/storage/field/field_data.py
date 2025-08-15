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

from beartype.typing import Generic, TypeVar, get_args

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

    def __validate_value(self, data_type: FieldDataType, value: FT) -> None:
        valid_types = FieldTypeConverter.get_valid_node_data_types(data_type)
        error_msg = "Invalid value {value} for the given field data type {data_type}"
        if not isinstance(value, tuple(valid_types)):
            raise InvalidInputException(error_msg.format(value=value, data_type=data_type))
        if isinstance(value, list):
            # Assuming list types have only 1 valid type
            valid_type = VALID_TYPE_BY_FIELD_DATA_TYPE[data_type][0]
            generic_type = get_args(valid_type)[0]
            if not all(isinstance(item, generic_type) for item in value):
                raise InvalidInputException(error_msg.format(value=value, data_type=data_type))

    @classmethod
    def from_field(cls, field: Field, value: FT) -> FieldData:
        return cls(field.data_type, field.name, value)


class VectorFieldData(FieldData[Vector]):
    def __init__(self, name: str, value: Vector) -> None:
        super().__init__(FieldDataType.VECTOR, name, value)
