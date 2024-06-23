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

from superlinked.framework.common.schema.general_type import T
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_factory import SchemaFactory


def schema(cls: type[T]) -> type[T] | type[IdSchemaObject]:
    """
    Use this decorator to annotate your class as a schema
    that can be used to represent your structured data.

    Schemas translate to entities in the embedding space
    that you can search by or search for.
    """
    return SchemaFactory().generate_schema(cls)
