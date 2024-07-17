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

from beartype.typing import get_args

from superlinked.framework.common.schema.event_schema_object import (
    CreatedAtField,
    SchemaReference,
)
from superlinked.framework.common.schema.exception import (
    FieldException,
    InvalidAttributeException,
    InvalidMemberException,
)
from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema_object import ConcreteSchemaField
from superlinked.framework.common.schema.schema_type import SchemaType
from superlinked.framework.common.util.generic_class_util import GenericClassUtil

valid_schema_field_types = {
    SchemaType.SCHEMA: ConcreteSchemaField | IdField,
    SchemaType.EVENT_SCHEMA: ConcreteSchemaField
    | IdField
    | CreatedAtField
    | SchemaReference,
}


class SchemaValidator:
    def __init__(self, schema_type: SchemaType) -> None:
        self.__schema_type = schema_type

    def check_class_attributes(self, cls: type[T]) -> None:
        for _, type_ in cls.__annotations__.items():
            type_ = GenericClassUtil.if_not_class_get_origin(type_)
            if not (
                issubclass(
                    type_,
                    get_args(valid_schema_field_types[self.__schema_type]),
                )
            ):
                raise InvalidAttributeException(
                    (
                        f"{'An event' if self.__schema_type == SchemaType.EVENT_SCHEMA else 'A'} ",
                        f"schema cannot have non-SchemaField attributes, got {type_.__name__}",
                    )
                )
        self.validate_id_field(cls)
        self.validate_created_at_field(cls)

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

    def __validate_field_single(
        self, cls: type[T], field_type: type, field_name: str
    ) -> None:
        field_names = [
            name
            for name, type_ in cls.__annotations__.items()
            if inspect.isclass(type_) and issubclass(type_, field_type)
        ]
        if len(field_names) != 1:
            raise FieldException(
                f"A schema must have exactly 1 {field_name}, got {len(field_names)} ({field_names})."
            )

    def validate_id_field(self, cls: type[T]) -> None:
        self.__validate_field_single(cls, IdField, "id")

    def validate_created_at_field(self, cls: type[T]) -> None:
        if self.__schema_type == SchemaType.EVENT_SCHEMA:
            self.__validate_field_single(cls, CreatedAtField, "created_at")
