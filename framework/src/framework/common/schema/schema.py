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

from __future__ import annotations

from beartype.typing import Sequence, cast
from typing_extensions import Self

from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_factory import SchemaFactory
from superlinked.framework.common.schema.schema_object import (
    SchemaField,
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_type import SchemaType

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["Schema"] = False


def schema(cls: type[T]) -> type[T] | type[IdSchemaObject]:
    """
    Use this decorator to annotate your class as a schema
    that can be used to represent your structured data.

    Schemas translate to entities in the embedding space
    that you can search by or search for.
    """
    return cast(
        type[T] | type[IdSchemaObject],
        SchemaFactory.decorate(cls, SchemaType.SCHEMA),
    )


class Schema(IdSchemaObject):
    """
    Inherit your schema class from this class to use as a schema
    that can be used to represent your structured data.

    Schemas translate to entities in the embedding space
    that you can search by or search for.
    """

    _id_field_name: str
    _schema_field_descriptors: list[SchemaFieldDescriptor]

    def __new__(cls) -> Self:
        schema_information = SchemaFactory._calculate_schema_information(
            cls, SchemaType.SCHEMA
        )
        instance = super().__new__(cls)
        instance._id_field_name = schema_information.id_field_name
        instance._schema_field_descriptors = schema_information.schema_field_descriptors
        return instance

    def __init__(self) -> None:
        base_cls: type = type(self)
        id_field_name: str = self._id_field_name
        super().__init__(base_cls, id_field_name)
        self._schema_fields = [
            self._init_field(schema_field_descriptor)
            for schema_field_descriptor in self._schema_field_descriptors
        ]

    def _get_schema_fields(self) -> Sequence[SchemaField]:
        """Returns all declared SchemaFields. Does not include the mandatory "id" field."""
        return self._schema_fields
