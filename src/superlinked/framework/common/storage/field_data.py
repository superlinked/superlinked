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

from typing import Generic, TypeVar

from superlinked.framework.common.data_types import NPArray, Vector
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data_type import FieldDataType
from superlinked.framework.common.storage.field_type_converter import FieldTypeConverter

# FieldType
FT = TypeVar("FT")


class FieldData(Field, Generic[FT]):
    def __init__(self, type_: FieldDataType, name: str, value: FT) -> None:
        super().__init__(type_, name)
        self.__validate_value(type_, value)
        self.value = value

    def __validate_value(self, data_type: FieldDataType, value: FT) -> None:
        valid_type = FieldTypeConverter.get_valid_python_types(data_type)
        if not isinstance(value, valid_type):
            raise ValueError(
                f"Invalid value {value} for the given field data type {data_type}"
            )

    @classmethod
    def from_field(cls, field: Field, value: FT) -> FieldData:
        return cls(field.data_type, field.name, value)


class BlobFieldData(FieldData[str]):
    def __init__(self, name: str, value: str) -> None:
        super().__init__(FieldDataType.BLOB, name, value)


class DoubleFieldData(FieldData[float]):
    def __init__(self, name: str, value: float) -> None:
        super().__init__(FieldDataType.DOUBLE, name, value)


class IntFieldData(FieldData[int]):
    def __init__(self, name: str, value: int) -> None:
        super().__init__(FieldDataType.INT, name, value)


class NPArrayFieldData(FieldData[NPArray]):
    def __init__(self, name: str, value: NPArray) -> None:
        super().__init__(FieldDataType.NPARRAY, name, value)


class StringFieldData(FieldData[str]):
    def __init__(self, name: str, value: str) -> None:
        super().__init__(FieldDataType.STRING, name, value)


class VectorFieldData(FieldData[Vector]):
    def __init__(self, name: str, value: Vector) -> None:
        super().__init__(FieldDataType.VECTOR, name, value)
