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
from types import UnionType

from beartype.typing import Sequence, cast

from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.schema_field_descriptor import (
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    SchemaField,
)

ID_FIELD_NAME = "id"


class IdSchemaObject(ABC):
    """
    Schema object with required ID field.
    """

    def __init__(self, base_cls: type, id_field_name: str) -> None:
        self._base_cls = base_cls
        self._schema_fields = self._init_schema_fields()
        self._schema_fields_by_name = {field.name: field for field in self._schema_fields}
        self.__id = IdField(self, id_field_name)
        if id_field_name != ID_FIELD_NAME:
            setattr(self, id_field_name, self.__id)

    @property
    def id(self) -> IdField:
        return self.__id

    @staticmethod
    def get_schema_field_type() -> UnionType:
        return cast(UnionType, ConcreteSchemaField)

    @abstractmethod
    def _init_schema_fields(self) -> Sequence[SchemaField]: ...

    @property
    def _base_class_name(self) -> str:
        return self._base_cls.__name__

    @property
    def _schema_name(self) -> str:
        return self._base_class_name

    @property
    def schema_fields(self) -> Sequence[SchemaField]:
        return self._schema_fields

    def _init_field(self, field_descriptor: SchemaFieldDescriptor) -> SchemaField:
        value = field_descriptor.type_(field_descriptor.name, self, field_descriptor.nullable)
        setattr(self, field_descriptor.name, value)
        return value

    def __str__(self) -> str:
        schema_fields = ", ".join([f"(name={field.name}, type={field.type_.__name__})" for field in self.schema_fields])
        return f"{type(self).__name__}(schema_name={self._schema_name}, schema_fields=[{schema_fields}])"
