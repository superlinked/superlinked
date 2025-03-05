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

from abc import ABC
from types import UnionType

from beartype.typing import TypeVar, cast

from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    SchemaObject,
)

IdSchemaObjectT = TypeVar("IdSchemaObjectT", bound="IdSchemaObject")
ID_FIELD_NAME = "id"


class IdSchemaObject(SchemaObject, ABC):
    """
    Schema object with required ID field.
    """

    def __init__(self, base_cls: type, id_field_name: str) -> None:
        super().__init__(base_cls)
        self.__id = IdField(self, id_field_name)
        if id_field_name != ID_FIELD_NAME:
            setattr(self, id_field_name, self.__id)

    @property
    def id(self) -> IdField:
        return self.__id

    @staticmethod
    def get_schema_field_type() -> UnionType:
        return cast(UnionType, ConcreteSchemaField)
