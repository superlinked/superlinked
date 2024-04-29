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

from typing import Generic, TypeVar

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data_type import FieldDataType

FT = TypeVar("FT")

VALID_TYPE_BY_FIELD_DATA_TYPE: dict[FieldDataType, type] = {
    FieldDataType.BLOB: str,
    FieldDataType.DOUBLE: float,
    FieldDataType.INT: int,
    FieldDataType.STRING: str,
    FieldDataType.VECTOR: Vector,
}


class FieldData(Field, Generic[FT]):
    def __init__(self, type_: FieldDataType, name: str, value: FT) -> None:
        super().__init__(type_, name)
        self.__validate_value(type_, value)
        self.value = value

    def __validate_value(self, type_: FieldDataType, value: FT) -> None:
        valid_type = VALID_TYPE_BY_FIELD_DATA_TYPE[type_]
        if not isinstance(value, valid_type):
            raise ValueError(
                f"Invalid value {value} for the given field data type {type_}"
            )


class BlobField(FieldData[str]):
    def __init__(self, name: str, value: str) -> None:
        super().__init__(FieldDataType.BLOB, name, value)


class DoubleField(FieldData[float]):
    def __init__(self, name: str, value: float) -> None:
        super().__init__(FieldDataType.DOUBLE, name, value)


class IntField(FieldData[int]):
    def __init__(self, name: str, value: int) -> None:
        super().__init__(FieldDataType.INT, name, value)


class StringField(FieldData[str]):
    def __init__(self, name: str, value: str) -> None:
        super().__init__(FieldDataType.STRING, name, value)


class VectorField(FieldData[Vector]):
    def __init__(self, name: str, value: Vector) -> None:
        super().__init__(FieldDataType.VECTOR, name, value)
