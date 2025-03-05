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

import inspect

from beartype.typing import Sequence, get_args

from superlinked.framework.common.schema.event_schema_object import (
    CREATED_AT_FIELD_NAME,
    CreatedAtField,
    SchemaReference,
)
from superlinked.framework.common.schema.exception import (
    FieldException,
    InvalidAttributeException,
    InvalidMemberException,
)
from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_schema_object import ID_FIELD_NAME, IdField
from superlinked.framework.common.schema.schema_field_descriptor import (
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_object import ConcreteSchemaField
from superlinked.framework.common.schema.schema_type import SchemaType

valid_schema_field_types = {
    SchemaType.SCHEMA: ConcreteSchemaField | IdField,
    SchemaType.EVENT_SCHEMA: ConcreteSchemaField | IdField | CreatedAtField | SchemaReference,
}


class SchemaValidator:
    def __init__(self, schema_type: SchemaType) -> None:
        self.__schema_type = schema_type

    def validate_class_attributes(self, schema_field_descriptors: Sequence[SchemaFieldDescriptor]) -> None:
        self.validate_field_types(schema_field_descriptors)
        self.validate_id_field(schema_field_descriptors)
        self.validate_created_at_field(schema_field_descriptors)
        if self.__schema_type == SchemaType.EVENT_SCHEMA and (
            optional_fields := [descriptor.name for descriptor in schema_field_descriptors if descriptor.nullable]
        ):
            raise InvalidAttributeException(f"An event schema cannot have optional attributes, got {optional_fields}")

    def validate_field_types(self, descriptors: Sequence[SchemaFieldDescriptor]) -> None:
        if wrong_annotation_types := [
            descriptor.type_.__name__
            for descriptor in descriptors
            if not (
                issubclass(
                    descriptor.type_,
                    get_args(valid_schema_field_types[self.__schema_type]),
                )
            )
        ]:
            raise InvalidAttributeException(
                (
                    f"{'An event' if self.__schema_type == SchemaType.EVENT_SCHEMA else 'A'} ",
                    f"schema cannot have non-SchemaField attributes, got {wrong_annotation_types}",
                )
            )

    def validate_id_field(self, descriptors: Sequence[SchemaFieldDescriptor]) -> None:
        self._validate_mandatory_single_field(descriptors, IdField, ID_FIELD_NAME)

    def validate_created_at_field(self, descriptors: Sequence[SchemaFieldDescriptor]) -> None:
        if self.__schema_type == SchemaType.EVENT_SCHEMA:
            self._validate_mandatory_single_field(descriptors, CreatedAtField, CREATED_AT_FIELD_NAME)

    def check_unannotated_members(self, cls: type[T]) -> None:
        base_members = dir(type("base_members", (object,), {}))
        base_members += ["__annotations__"]
        for t in inspect.getmembers(cls):
            if t[0] not in base_members:
                raise InvalidMemberException(
                    (
                        f"{'Schema' if self.__schema_type == SchemaType.SCHEMA else 'Event schema'} ",
                        f"cannot have functions nor instantiated attributes, got {type(t[1]).__name__} {t[0]}.",
                    )
                )

    def _validate_mandatory_single_field(
        self, descriptors: Sequence[SchemaFieldDescriptor], field_type: type, field_name: str
    ) -> None:
        field_names = [
            descriptor.name
            for descriptor in descriptors
            if inspect.isclass(descriptor.type_)
            and issubclass(descriptor.type_, field_type)
            and not descriptor.nullable
        ]
        if len(field_names) != 1:
            raise FieldException(f"A schema must have exactly 1 {field_name}, got {len(field_names)} ({field_names}).")
        if field_name not in field_names and any(
            descriptor.name for descriptor in descriptors if descriptor.name == field_name
        ):
            field_type_name = field_type.__name__
            raise FieldException(f"A schema cannot have a non-{field_type_name} named '{field_name}'.")
