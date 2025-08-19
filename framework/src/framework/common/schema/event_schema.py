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


from beartype.typing import Sequence
from typing_extensions import Self, override

from superlinked.framework.common.schema.event_schema_object import (
    CreatedAtField,
    EventSchemaObject,
)
from superlinked.framework.common.schema.schema_factory import SchemaFactory
from superlinked.framework.common.schema.schema_field_descriptor import (
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.schema.schema_type import SchemaType


class EventSchema(EventSchemaObject):
    _id_field_name: str
    _created_at_field_name: str
    _schema_field_descriptors: list[SchemaFieldDescriptor]

    def __new__(cls) -> Self:
        schema_information = SchemaFactory.calculate_schema_information(cls, SchemaType.EVENT_SCHEMA)
        instance = super().__new__(cls)
        instance._id_field_name = schema_information.id_field_name
        instance._created_at_field_name = SchemaFactory.get_field_name_or_raise(cls, CreatedAtField)
        instance._schema_field_descriptors = schema_information.schema_field_descriptors
        return instance

    def __init__(self) -> None:
        super().__init__(type(self), self._id_field_name, self._created_at_field_name)

    @override
    def _init_schema_fields(self) -> Sequence[SchemaField]:
        """Returns all declared SchemaFields. Does not include the mandatory "id" and "created_at" fields."""
        return [self._init_field(schema_field_descriptor) for schema_field_descriptor in self._schema_field_descriptors]
