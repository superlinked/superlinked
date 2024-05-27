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

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.storage.exception import EncoderException
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData
from superlinked.framework.common.storage.field_data_type import FieldDataType

# Encoded type
ET = TypeVar("ET")


class FieldEncoder(ABC, Generic[ET]):
    def __init__(self) -> None:
        self._encode_map: dict[FieldDataType, Callable[..., ET]] = {
            FieldDataType.BLOB: self._encode_blob,
            FieldDataType.DOUBLE: self._encode_double,
            FieldDataType.INT: self._encode_int,
            FieldDataType.FLOAT_LIST: self._encode_float_list,
            FieldDataType.STRING: self._encode_string,
            FieldDataType.VECTOR: self._encode_vector,
        }
        self._decode_map: dict[FieldDataType, Callable[[ET], Any]] = {
            FieldDataType.BLOB: self._decode_blob,
            FieldDataType.DOUBLE: self._decode_double,
            FieldDataType.INT: self._decode_int,
            FieldDataType.FLOAT_LIST: self._decode_float_list,
            FieldDataType.STRING: self._decode_string,
            FieldDataType.VECTOR: self._decode_vector,
        }

    @abstractmethod
    def _encode_blob(self, blob: str) -> ET:
        pass

    @abstractmethod
    def _decode_blob(self, blob: ET) -> str:
        pass

    @abstractmethod
    def _encode_double(self, double: float) -> ET:
        pass

    @abstractmethod
    def _decode_double(self, double: ET) -> float:
        pass

    @abstractmethod
    def _encode_int(self, int_: int) -> ET:
        pass

    @abstractmethod
    def _decode_int(self, int_: ET) -> int:
        pass

    @abstractmethod
    def _encode_float_list(self, float_list: list[float]) -> ET:
        pass

    @abstractmethod
    def _decode_float_list(self, float_list: ET) -> list[float]:
        pass

    @abstractmethod
    def _encode_string(self, string: str) -> ET:
        pass

    @abstractmethod
    def _decode_string(self, string: ET) -> str:
        pass

    @abstractmethod
    def _encode_vector(self, vector: Vector) -> ET:
        pass

    @abstractmethod
    def _decode_vector(self, vector: ET) -> Vector:
        pass

    def encode_field(self, field: FieldData) -> ET:
        if encoder := self._encode_map.get(field.data_type):
            return encoder(field.value)
        raise EncoderException(
            f"Unknown field type: {field.data_type}, cannot encode field."
        )

    def decode_field(self, field: Field, value: ET) -> FieldData:
        if decoder := self._decode_map.get(field.data_type):
            return FieldData.from_field(field, decoder(value))
        raise EncoderException(
            f"Unknown field type: {field.data_type}, cannot decode field."
        )
