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


import json

from beartype.typing import Any, Callable

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import NotImplementedException
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.field.field_data_type import FieldDataType

TopKEncodedTypes = str | float | int | list[float] | bytes | bool


class TopKFieldEncoder:
    def __init__(self) -> None:
        self._encode_map: dict[FieldDataType, Callable[..., Any]] = {
            FieldDataType.BLOB: self._encode_blob,
            FieldDataType.DOUBLE: self._encode_double,
            FieldDataType.FLOAT_LIST: self._encode_float_list,
            FieldDataType.INT: self._encode_int,
            FieldDataType.JSON: self._encode_json,
            FieldDataType.STRING: self._encode_string,
            FieldDataType.METADATA_STRING: self._encode_string,
            FieldDataType.STRING_LIST: self._encode_string_list,
            FieldDataType.VECTOR: self._encode_vector,
            FieldDataType.BOOLEAN: self._encode_bool,
        }
        self._decode_map: dict[FieldDataType, Callable[..., Any]] = {
            FieldDataType.BLOB: self._decode_blob,
            FieldDataType.DOUBLE: self._decode_double,
            FieldDataType.FLOAT_LIST: self._decode_float_list,
            FieldDataType.INT: self._decode_int,
            FieldDataType.JSON: self._decode_json,
            FieldDataType.STRING: self._decode_string,
            FieldDataType.METADATA_STRING: self._decode_string,
            FieldDataType.STRING_LIST: self._decode_string_list,
            FieldDataType.VECTOR: self._decode_vector,
            FieldDataType.BOOLEAN: self._decode_bool,
        }

    def _encode_blob(self, blob: BlobInformation) -> str | None:
        return blob.path

    def _decode_blob(self, blob: bytes) -> BlobInformation:
        return BlobInformation(path=blob.decode("utf-8"))

    def _encode_double(self, double: float) -> float:
        return float(double)

    def _decode_double(self, double: float) -> float:
        return float(double)

    def _encode_float_list(self, float_list: list[float]) -> list[float]:
        return self._encode_vector(Vector(float_list))

    def _decode_float_list(self, float_list: list[float]) -> list[float]:
        vector = self._decode_vector(float_list)
        return [float(x) for x in vector.value.tolist()]

    def _encode_int(self, int_: int) -> int:
        return int_

    def _decode_int(self, int_: str) -> int:
        return int(int_)

    def _encode_bool(self, bool_: bool) -> bool:
        return bool(bool_)

    def _decode_bool(self, bool_: str) -> bool:
        return bool(bool_)

    def _encode_json(self, json_: dict[str, Any]) -> str:
        return json.dumps(json_, ensure_ascii=True)

    def _decode_json(self, json_: str) -> dict[str, Any]:
        return json.loads(json_) if json_ else {}

    def _encode_string(self, string: str) -> str:
        return string

    def _decode_string(self, string: str) -> str:
        return string

    def _encode_string_list(self, string_list: list[str]) -> str:
        return ", ".join(string_list)

    def _decode_string_list(self, string_list: str) -> list[str]:
        return string_list.split(", ")

    def _encode_vector(self, vector: Vector) -> list[float]:
        return list(vector.value.tolist())

    def _decode_vector(self, vector: list[float]) -> Vector:
        return Vector(vector)

    def encode_field(self, field: FieldData) -> TopKEncodedTypes:
        if encoder := self._encode_map.get(field.data_type):
            return encoder(field.value)
        raise NotImplementedException("Unknown field type.", field_type=field.data_type.name)

    def decode_field(self, field: Field, value: str) -> FieldData:
        if decoder := self._decode_map.get(field.data_type):
            return FieldData.from_field(field, decoder(value))
        raise NotImplementedException("Unknown field type.", field_type=field.data_type.name)
