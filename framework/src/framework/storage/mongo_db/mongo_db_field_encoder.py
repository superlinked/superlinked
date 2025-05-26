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
from beartype.typing import Any, Callable, Sequence

from superlinked.framework.common.data_types import Json, Vector
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.storage.exception import EncoderException
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.search_index.vector_component_precision import (
    VectorComponentPrecision,
)

MongoDBEncodedTypes = str | float | int | Sequence[float]


class MongoDBFieldEncoder:
    def __init__(self) -> None:
        self._encode_map: dict[FieldDataType, Callable[..., Any]] = {
            FieldDataType.BLOB: self._encode_blob,
            FieldDataType.DOUBLE: self._encode_double,
            FieldDataType.FLOAT_LIST: self._encode_float_list,
            FieldDataType.INT: self._encode_int,
            FieldDataType.BOOLEAN: self._encode_boolean,
            FieldDataType.JSON: self._encode_json,
            FieldDataType.STRING: self._encode_string,
            FieldDataType.METADATA_STRING: self._encode_string,
            FieldDataType.STRING_LIST: self._encode_string_list,
            FieldDataType.VECTOR: self._encode_vector,
        }
        self._decode_map: dict[FieldDataType, Callable[[Any], Any]] = {
            FieldDataType.BLOB: self._decode_blob,
            FieldDataType.DOUBLE: self._decode_double,
            FieldDataType.FLOAT_LIST: self._decode_float_list,
            FieldDataType.INT: self._decode_int,
            FieldDataType.BOOLEAN: self._decode_boolean,
            FieldDataType.JSON: self._decode_json,
            FieldDataType.STRING: self._decode_string,
            FieldDataType.METADATA_STRING: self._encode_string,
            FieldDataType.STRING_LIST: self._decode_string_list,
            FieldDataType.VECTOR: self._decode_vector,
        }
        self.__vector_precision_type = VectorComponentPrecision.init_from_settings().to_np_type()

    def _encode_blob(self, blob: BlobInformation) -> str | None:
        return blob.path

    def _decode_blob(self, blob: str) -> BlobInformation:
        return BlobInformation(path=blob)

    def _encode_double(self, double: float) -> float:
        return double

    def _decode_double(self, double: float) -> float:
        return double

    def _encode_float_list(self, float_list: Sequence[float]) -> Sequence[float]:
        return float_list

    def _decode_float_list(self, float_list: Sequence[float]) -> Sequence[float]:
        return float_list

    def _encode_int(self, int_: int) -> int:
        return int_

    def _decode_int(self, int_: int) -> int:
        return int_

    def _encode_boolean(self, bool_: bool) -> bool:
        return bool_

    def _decode_boolean(self, bool_: bool) -> bool:
        return bool_

    def _encode_json(self, json_: Json) -> str:
        return json.dumps(json_, ensure_ascii=True)

    def _decode_json(self, json_: str) -> Json:
        return json.loads(json_) if json_ else {}

    def _encode_string(self, string: str) -> str:
        return string

    def _decode_string(self, string: str) -> str:
        return string

    def _encode_string_list(self, string_list: Sequence[str]) -> Sequence[str]:
        return string_list

    def _decode_string_list(self, string_list: Sequence[str]) -> Sequence[str]:
        return string_list

    def _encode_vector(self, vector: Vector) -> Sequence[float]:
        return vector.value.astype(self.__vector_precision_type).tolist()

    def _decode_vector(self, vector: Any) -> Vector:
        if not isinstance(vector, list):
            raise NotImplementedError(f"Cannot decode non-list type vector, got: {type(vector)}")
        return Vector(np.array(vector).astype(self.__vector_precision_type).tolist())

    def encode_field(self, field: FieldData) -> MongoDBEncodedTypes:
        if encoder := self._encode_map.get(field.data_type):
            return encoder(field.value)
        raise EncoderException(f"Unknown field type: {field.data_type}, cannot encode field.")

    def decode_field(self, field: Field, value: MongoDBEncodedTypes) -> FieldData:
        if decoder := self._decode_map.get(field.data_type):
            return FieldData.from_field(field, decoder(value))
        raise EncoderException(f"Unknown field type: {field.data_type}, cannot decode field.")
