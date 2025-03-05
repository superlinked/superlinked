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
from types import NoneType, UnionType

from beartype.typing import Sequence, Union, get_args

from superlinked.framework.common.schema.event_schema_object import (
    CreatedAtField,
    EventSchemaObject,
)
from superlinked.framework.common.schema.exception import InvalidAttributeException
from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_field_descriptor import (
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_object import SchemaField
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
    def calculate_schema_information(schema_cls: type[T], schema_type: SchemaType) -> SchemaInformation:
        schema_validator = SchemaValidator(schema_type)
        base_class = IdSchemaObject if schema_type == SchemaType.SCHEMA else EventSchemaObject
        schema_field_descriptors = [
            SchemaFactory.compile_annotation(name, type_annotation)
            for name, type_annotation in schema_cls.__annotations__.items()
        ]
        schema_validator.validate_class_attributes(schema_field_descriptors)
        schema_field_descriptors = SchemaFactory.filter_schema_field_descriptors(schema_field_descriptors, base_class)
        return SchemaInformation(
            SchemaFactory.get_field_name_or_raise(schema_cls, IdField), schema_field_descriptors, base_class
        )

    @staticmethod
    def compile_annotation(name: str, type_annotation: type) -> SchemaFieldDescriptor:
        type_ = GenericClassUtil.if_not_class_get_origin(type_annotation)
        arg_types = get_args(type_annotation)
        if type_ is UnionType or type_ is Union:
            non_none_arg_types = [arg_type for arg_type in arg_types if arg_type is not NoneType]
            if len(non_none_arg_types) != 1:
                raise InvalidAttributeException(
                    "An attribute of a schema can only have one optional or mandatory type-annotation, "
                    + f"{name} got {[arg_type.__name__ for arg_type in non_none_arg_types]}"
                )
            return SchemaFieldDescriptor(
                name=name,
                type_=next(iter(non_none_arg_types), None.__class__),
                nullable=len(arg_types) != 1,
                arg_types=arg_types,
            )
        return SchemaFieldDescriptor(name=name, type_=type_, nullable=False, arg_types=arg_types)

    @staticmethod
    def filter_schema_field_descriptors(
        descriptors: Sequence[SchemaFieldDescriptor], base_class: type[IdSchemaObject | EventSchemaObject]
    ) -> list[SchemaFieldDescriptor]:
        return [
            descriptor
            for descriptor in descriptors
            if issubclass(descriptor.type_, get_args(base_class.get_schema_field_type()))
        ]

    @staticmethod
    def get_field_name_or_raise(schema_cls: type[T], field_type: type) -> str:
        return next(
            name
            for name, type_ in schema_cls.__annotations__.items()
            if inspect.isclass(type_) and issubclass(type_, field_type)
        )

    @staticmethod
    def decorate(schema_cls: type[T], schema_type: SchemaType) -> type[IdSchemaObject | EventSchemaObject]:
        SchemaValidator(schema_type).check_unannotated_members(schema_cls)
        schema_information = SchemaFactory.calculate_schema_information(schema_cls, schema_type)

        class Decorated(schema_information.base_class):  # type: ignore
            def __init__(self) -> None:
                if schema_information.base_class is EventSchemaObject:
                    created_at_field_name = SchemaFactory.get_field_name_or_raise(schema_cls, CreatedAtField)
                    super().__init__(
                        schema_cls,
                        schema_information.id_field_name,
                        created_at_field_name,
                    )
                else:
                    super().__init__(schema_cls, schema_information.id_field_name)

            def _init_schema_fields(self) -> Sequence[SchemaField]:
                """Returns all declared SchemaFields. Does not include the mandatory "id" field."""
                return [
                    self._init_field(schema_field_descriptor)
                    for schema_field_descriptor in schema_information.schema_field_descriptors
                ]

        return Decorated
