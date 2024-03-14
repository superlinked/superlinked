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

from typing_extensions import override

from superlinked.framework.common.schema.exception import InvalidAttributeException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import (
    SchemaField,
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_reference import SchemaReference


class EventSchemaObject(IdSchemaObject):
    """
    Custom decorated event schema class.
    Event schemas can be used to reference other schema and to define interactions between schemas.
    """

    @override
    def _init_field(self, field_descriptor: SchemaFieldDescriptor) -> SchemaField:
        if field_descriptor.type_ == SchemaReference:
            if len(field_descriptor.type_args) != 1:
                raise InvalidAttributeException(
                    (
                        f"Badly annotated SchemaReference ({field_descriptor.type_args}). ",
                        "SchemaReference should be annotated with the referred schema object type.",
                    )
                )
            value: SchemaReference = SchemaReference(
                field_descriptor.name, self, field_descriptor.type_args[0]
            )
            setattr(self, field_descriptor.name, value)
            return value
        return super()._init_field(field_descriptor)
