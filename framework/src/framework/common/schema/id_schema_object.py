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

from types import UnionType

from beartype.typing import Sequence, TypeVar, cast

from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    SchemaField,
    SchemaObject,
    SchemaObjectT,
)

IdSchemaObjectT = TypeVar("IdSchemaObjectT", bound="IdSchemaObject")


class IdField(SchemaField[str]):
    """
    A class representing an ID field in a schema object.
    """

    def __init__(self, schema_obj: SchemaObjectT, id_field_name: str) -> None:
        super().__init__(id_field_name, schema_obj, str)

    @staticmethod
    def combine_values(values: Sequence[str]) -> str:
        return ", ".join(values)


class IdSchemaObject(SchemaObject):
    """
    Schema object with required ID field.
    """

    def __init__(self, base_cls: type, id_field_name: str) -> None:
        super().__init__(base_cls)
        self.__id = IdField(self, id_field_name)

    @property
    def id(self) -> IdField:
        return self.__id

    @staticmethod
    def get_schema_field_type() -> UnionType:
        return cast(UnionType, ConcreteSchemaField)
