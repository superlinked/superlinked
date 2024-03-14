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

from typing import cast, get_args

from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_decorator import SchemaDecorator
from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_reference import SchemaReference
from superlinked.framework.common.schema.schema_type import SchemaType
from superlinked.framework.common.schema.schema_validator import SchemaValidator
from superlinked.framework.common.util.schema_util import SchemaUtil


class SchemaFactory:
    def __init__(self) -> None:
        self.__schema_validators = {
            SchemaType.SCHEMA: SchemaValidator(SchemaType.SCHEMA),
            SchemaType.EVENT_SCHEMA: SchemaValidator(SchemaType.EVENT_SCHEMA),
        }
        self.__schema_field_types = {
            SchemaType.SCHEMA: ConcreteSchemaField,
            SchemaType.EVENT_SCHEMA: ConcreteSchemaField | SchemaReference,
        }

    def __generate(
        self, cls: type[T], schema_type: SchemaType
    ) -> type[T] | IdSchemaObject | EventSchemaObject:
        schema_validator = self.__schema_validators[schema_type]
        schema_validator.check_class_attributes(cls)
        schema_validator.check_unannotated_members(cls)
        schema_name: str = cls.__name__
        schema_field_descriptors = list[SchemaFieldDescriptor]()
        for name, type_ in cls.__annotations__.items():
            type_args = get_args(type_)
            type_ = SchemaUtil.if_not_class_get_origin(type_)
            if not type_:
                continue
            if issubclass(
                type_,
                get_args(self.__schema_field_types[schema_type]),
            ):
                schema_field_descriptors.append(
                    SchemaFieldDescriptor(name, type_, type_args)
                )
        return SchemaDecorator.decorate(
            cls, schema_type, schema_name, schema_field_descriptors, schema_validator
        )

    def generate_schema(self, cls: type[T]) -> type[T] | type[IdSchemaObject]:
        return cast(
            type[T] | type[IdSchemaObject], self.__generate(cls, SchemaType.SCHEMA)
        )

    def generate_event_schema(self, cls: type[T]) -> type[T] | type[EventSchemaObject]:
        return cast(
            type[T] | type[EventSchemaObject],
            self.__generate(cls, SchemaType.EVENT_SCHEMA),
        )
