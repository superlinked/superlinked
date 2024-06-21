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

from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.schema import T
from superlinked.framework.common.schema.schema_factory import SchemaFactory


def event_schema(cls: type[T]) -> type[T] | type[EventSchemaObject]:
    """
    Use this decorator to annotate your class as an event schema
    that can be used to represent events between other schemas.
    """
    return SchemaFactory().generate_event_schema(cls)
