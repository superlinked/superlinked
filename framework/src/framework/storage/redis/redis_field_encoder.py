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

import numpy as np
from beartype.typing import Any, Callable, cast

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InvalidStateException,
    NotImplementedException,
)
from superlinked.framework.common.precision import Precision
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.field.field_data_type import FieldDataType

RedisEncodedTypes = str | float | int | list[float] | bytes


class RedisFieldEncoder:
    def __init__(self, vector_precision: Precision) -> None:
        self._encode_map: dict[FieldDataType, Callable[..., Any]] = {
            FieldDataType.BLOB: self._encode_blob,
            FieldDataType.DOUBLE: self._encode_double,
            FieldDataType.FLOAT_LIST: self._encode_float_list,
            FieldDataType.INT: self._encode_int,
            FieldDataType.BOOLEAN: self._encode_bool,
            FieldDataType.JSON: self._encode_json,
            FieldDataType.STRING: self._encode_string,
            FieldDataType.METADATA_STRING: self._encode_string,
            FieldDataType.STRING_LIST: self._encode_string_list,
            FieldDataType.VECTOR: self._encode_vector,
        }
        self._decode_map: dict[FieldDataType, Callable[[bytes], Any]] = {
            FieldDataType.BLOB: self._decode_blob,
            FieldDataType.DOUBLE: self._decode_double,
            FieldDataType.FLOAT_LIST: self._decode_float_list,
            FieldDataType.INT: self._decode_int,
            FieldDataType.BOOLEAN: self._decode_bool,
            FieldDataType.JSON: self._decode_json,
            FieldDataType.STRING: self._decode_string,
            FieldDataType.METADATA_STRING: self._decode_string,
            FieldDataType.STRING_LIST: self._decode_string_list,
            FieldDataType.VECTOR: self._decode_vector,
        }
        self.__vector_precision_type = vector_precision.to_np_type()

    def _encode_blob(self, blob: BlobInformation) -> str | None:
        return blob.path

    def _decode_blob(self, blob: bytes) -> BlobInformation:
        return BlobInformation(path=blob.decode("utf-8"))

    def _encode_double(self, double: float) -> float:
        return double

    def _decode_double(self, double: bytes) -> float:
        return float(double)

    def _encode_float_list(self, float_list: list[float]) -> bytes:
        return self._encode_vector(Vector(float_list))

    def _decode_float_list(self, float_list: bytes) -> list[float]:
        vector = self._decode_vector(float_list)
        return [float(x) for x in vector.value.tolist()]

    def _encode_int(self, int_: int) -> int:
        return int_

    def _decode_int(self, int_: bytes) -> int:
        return int(int_)

    def _encode_bool(self, bool_: bool) -> str:
        return "1" if bool_ else "0"

    def _decode_bool(self, bool_: bytes) -> bool:
        return bool(int(bool_))

    def _encode_json(self, json_: dict[str, Any]) -> str:
        return json.dumps(json_, ensure_ascii=True)

    def _decode_json(self, json_: bytes) -> dict[str, Any]:
        return json.loads(json_.decode("utf-8")) if json_ else {}

    def _encode_string(self, string: str) -> str:
        return string

    def _decode_string(self, string: bytes) -> str:
        return string.decode("utf-8")

    def _encode_string_list(self, string_list: list[str]) -> bytes:
        return str.encode(", ".join(string_list), "utf-8")

    def _decode_string_list(self, string_list: bytes) -> list[str]:
        decoded = string_list.decode("utf-8")
        return decoded.split(", ") if decoded else []

    def _encode_vector(self, vector: Vector) -> bytes:
        np_vector: np.ndarray
        if isinstance(vector.value, np.ndarray):
            np_vector = vector.value.astype(self.__vector_precision_type)
        else:
            np_vector = np.array(vector.value, dtype=self.__vector_precision_type)
        return np_vector.tobytes()

    def _decode_vector(self, vector: bytes) -> Vector:
        if not isinstance(vector, bytes):
            raise InvalidStateException("Cannot decode non-bytes type vector.", vector_type=type(vector))
        return Vector(np.frombuffer(vector, self.__vector_precision_type).tolist())

    def encode_field(self, field: FieldData) -> RedisEncodedTypes:
        if encoder := self._encode_map.get(field.data_type):
            return encoder(field.value)
        raise NotImplementedException("Unknown field type.", field_type=field.data_type.name)

    def decode_field(self, field: Field, value: bytes | None) -> FieldData:
        if value is None:
            return FieldData(FieldDataType.NULL, field.name, None)
        if decoder := self._decode_map.get(field.data_type):
            return FieldData.from_field(field, decoder(value))
        raise NotImplementedException("Unknown field type.", field_type=field.data_type.name)

    def convert_bytes_keys_dict(self, data: dict[bytes, Any]) -> dict[str, Any]:
        return {self._decode_string(cast(bytes, key)): self.convert_bytes_keys(value) for key, value in data.items()}

    def convert_bytes_keys(self, data: Any) -> Any:
        if isinstance(data, dict):
            return self.convert_bytes_keys_dict(data)
        if isinstance(data, list):
            return [self.convert_bytes_keys(item) for item in data]
        if isinstance(data, tuple):
            return tuple(self.convert_bytes_keys(item) for item in data)
        return data

    def decode_redis_id_to_entity_id(self, encoded_redis_id: bytes) -> EntityId:
        decoded_redis_id = self._decode_string(encoded_redis_id)
        schema_id, object_id = decoded_redis_id.split(":", 1)
        return EntityId(schema_id=schema_id, object_id=object_id)

    def encode_entity_id_to_redis_id(self, entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"
