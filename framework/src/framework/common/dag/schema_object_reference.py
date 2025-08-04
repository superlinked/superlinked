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

from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.schema.event_schema_object import SchemaReference
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject


class SchemaObjectReference:
    def __init__(self, schema: IdSchemaObject, reference_field: SchemaReference) -> None:
        if not isinstance(schema, reference_field._referenced_schema):
            raise InvalidStateException(f"{type(self).__name__}'s schema is not the referenced schema.")
        self.schema = schema
        self.reference_field = reference_field

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(schema={self.schema._schema_name}, reference_field={self.reference_field})"
