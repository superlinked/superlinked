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
from dataclasses import dataclass

from beartype.typing import get_args

from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_schema_object import IdField, IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaFieldDescriptor
from superlinked.framework.common.schema.schema_type import SchemaType
from superlinked.framework.common.schema.schema_validator import SchemaValidator
from superlinked.framework.common.util.generic_class_util import GenericClassUtil


@dataclass(frozen=True)
class SchemaInformation:
    id_field_name: str
    schema_field_descriptors: list[SchemaFieldDescriptor]
    base_class: type[IdSchemaObject | EventSchemaObject]


class SchemaFactory:

    @staticmethod
    def _calculate_schema_information(
        schema_cls: type[T], schema_type: SchemaType
    ) -> SchemaInformation:
        schema_validator = SchemaValidator(schema_type)
        schema_validator.check_class_attributes(schema_cls)
        base_class = (
            IdSchemaObject if schema_type == SchemaType.SCHEMA else EventSchemaObject
        )
        schema_field_descriptors = SchemaFactory.calculate_schema_field_descriptors(
            schema_cls, base_class
        )
        return SchemaInformation(
            SchemaFactory.get_field_name_or_raise(schema_cls, IdField),
            schema_field_descriptors,
            base_class,
        )

    @staticmethod
    def get_field_name_or_raise(schema_cls: type[T], field_type: type) -> str:
        return next(
            name
            for name, type_ in schema_cls.__annotations__.items()
            if inspect.isclass(type_) and issubclass(type_, field_type)
        )

    @staticmethod
    def calculate_schema_field_descriptors(
        schema_cls: type[T], base_class: type[IdSchemaObject | EventSchemaObject]
    ) -> list[SchemaFieldDescriptor]:
        return [
            SchemaFieldDescriptor(name, origin, get_args(type_))
            for name, type_ in schema_cls.__annotations__.items()
            if (origin := GenericClassUtil.if_not_class_get_origin(type_))
            and issubclass(origin, get_args(base_class.get_schema_field_type()))
        ]
