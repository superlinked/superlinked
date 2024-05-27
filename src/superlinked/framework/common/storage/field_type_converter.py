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

from typing import Any, cast

from beartype.typing import Sequence

from superlinked.framework.common.data_types import PythonTypes, Vector
from superlinked.framework.common.schema.schema_object import (
    Array,
    ConcreteSchemaField,
    Float,
    Integer,
    SchemaField,
    String,
    Timestamp,
)
from superlinked.framework.common.storage.field_data_type import FieldDataType
from superlinked.framework.common.util.generic_class_util import GenericClassUtil

FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE: dict[type[ConcreteSchemaField], FieldDataType] = {
    Array: FieldDataType.FLOAT_LIST,
    Float: FieldDataType.DOUBLE,
    Integer: FieldDataType.INT,
    String: FieldDataType.STRING,
    Timestamp: FieldDataType.INT,
}

FIELD_DATA_TYPE_BY_PYTHON_TYPE: dict[type[PythonTypes], FieldDataType] = {
    float: FieldDataType.DOUBLE,
    int: FieldDataType.INT,
    str: FieldDataType.STRING,
    list[float]: FieldDataType.FLOAT_LIST,
    Vector: FieldDataType.VECTOR,
}

VALID_TYPE_BY_FIELD_DATA_TYPE: dict[FieldDataType, Sequence[type[PythonTypes]]] = {
    FieldDataType.BLOB: [str],
    FieldDataType.DOUBLE: [int, float],
    FieldDataType.INT: [int],
    FieldDataType.FLOAT_LIST: [list[float]],
    FieldDataType.STRING: [str],
    FieldDataType.VECTOR: [Vector],
}


class FieldTypeConverter:
    @staticmethod
    def convert_schema_field_type(
        schema_field_cls: type[SchemaField[Any]],
    ) -> FieldDataType:
        if field_data_type := FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE.get(
            cast(type[ConcreteSchemaField], schema_field_cls)
        ):
            return field_data_type
        raise NotImplementedError(
            f"Unknown schema field type: {schema_field_cls.__name__}"
        )

    @staticmethod
    def convert_python_type(type_: type[PythonTypes]) -> FieldDataType:
        if field_data_type := FIELD_DATA_TYPE_BY_PYTHON_TYPE.get(
            cast(type[PythonTypes], type_)
        ):
            return field_data_type
        raise NotImplementedError(f"Unknown python type: {type_}")

    @staticmethod
    def get_valid_python_types(data_type: FieldDataType) -> Sequence[type[PythonTypes]]:
        return [
            GenericClassUtil.if_not_class_get_origin(type_)
            for type_ in VALID_TYPE_BY_FIELD_DATA_TYPE[data_type]
        ]
