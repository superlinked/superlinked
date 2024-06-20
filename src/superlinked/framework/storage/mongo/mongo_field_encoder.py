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

import numpy as np
from beartype.typing import Any, Callable, Sequence

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.storage.exception import EncoderException
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData
from superlinked.framework.common.storage.field_data_type import FieldDataType

MongoEncodedTypes = str | float | int | Sequence[float]


class MongoFieldEncoder:
    def __init__(self) -> None:
        # TODO FAI-1909
        self._encode_map: dict[FieldDataType, Callable[..., Any]] = {
            FieldDataType.BLOB: self._encode_blob,
            FieldDataType.DOUBLE: self._encode_double,
            FieldDataType.FLOAT_LIST: self._encode_float_list,
            FieldDataType.INT: self._encode_int,
            FieldDataType.STRING: self._encode_string,
            FieldDataType.STRING_LIST: self._encode_string_list,
            FieldDataType.VECTOR: self._encode_vector,
        }
        self._decode_map: dict[FieldDataType, Callable[[Any], Any]] = {
            FieldDataType.BLOB: self._decode_blob,
            FieldDataType.DOUBLE: self._decode_double,
            FieldDataType.FLOAT_LIST: self._decode_float_list,
            FieldDataType.INT: self._decode_int,
            FieldDataType.STRING: self._decode_string,
            FieldDataType.STRING_LIST: self._decode_string_list,
            FieldDataType.VECTOR: self._decode_vector,
        }

    def _encode_blob(self, blob: str) -> str:
        return blob

    def _decode_blob(self, blob: str) -> str:
        return blob

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

    def _encode_string(self, string: str) -> str:
        return string

    def _decode_string(self, string: str) -> str:
        return string

    def _encode_string_list(self, string_list: Sequence[str]) -> Sequence[str]:
        return string_list

    def _decode_string_list(self, string_list: Sequence[str]) -> Sequence[str]:
        return string_list

    def _encode_vector(self, vector: Vector) -> Sequence[float]:
        return vector.value.astype(np.float32).tolist()

    def _decode_vector(self, vector: Any) -> Vector:
        if not isinstance(vector, list):
            raise NotImplementedError(
                f"Cannot decode non-list type vector, got: {type(vector)}"
            )
        return Vector(np.array(vector).astype(np.float32).tolist())

    def encode_field(self, field: FieldData) -> MongoEncodedTypes:
        if encoder := self._encode_map.get(field.data_type):
            return encoder(field.value)
        raise EncoderException(
            f"Unknown field type: {field.data_type}, cannot encode field."
        )

    def decode_field(self, field: Field, value: MongoEncodedTypes) -> FieldData:
        if decoder := self._decode_map.get(field.data_type):
            return FieldData.from_field(field, decoder(value))
        raise EncoderException(
            f"Unknown field type: {field.data_type}, cannot decode field."
        )
