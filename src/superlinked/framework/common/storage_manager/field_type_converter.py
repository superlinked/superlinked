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

from superlinked.framework.common.data_types import Vector
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

FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE: dict[type[ConcreteSchemaField], FieldDataType] = {
    Array: FieldDataType.VECTOR,
    Float: FieldDataType.DOUBLE,
    Integer: FieldDataType.INT,
    String: FieldDataType.STRING,
    Timestamp: FieldDataType.INT,
}

PytonTypes = float | int | str | Vector

FIELD_DATA_TYPE_BY_PYTHON_TYPE: dict[type[PytonTypes], FieldDataType] = {
    float: FieldDataType.INT,
    int: FieldDataType.DOUBLE,
    str: FieldDataType.STRING,
    Vector: FieldDataType.INT,
}


class FieldTypeConverter:
    def convert_schema_field_type(
        self, schema_field_cls: type[SchemaField[Any]]
    ) -> FieldDataType:
        if field_data_type := FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE.get(
            cast(type[ConcreteSchemaField], schema_field_cls)
        ):
            return field_data_type
        raise NotImplementedError(
            f"Unknown schema field type: {schema_field_cls.__name__}"
        )

    def convert_python_type(self, type_: type) -> FieldDataType:
        if field_data_type := FIELD_DATA_TYPE_BY_PYTHON_TYPE.get(
            cast(type[PytonTypes], type_)
        ):
            return field_data_type
        raise NotImplementedError(f"Unknown python type: {type_}")
