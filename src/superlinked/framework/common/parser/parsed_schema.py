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

from dataclasses import dataclass
from typing import Generic

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SFT, SchemaField


class ParsedSchemaField(Generic[SFT]):
    def __init__(self, schema_field: SchemaField[SFT], value: SFT) -> None:
        self.schema_field = schema_field
        self.value = value

    @classmethod
    def from_schema_field(
        cls, schema_field: SchemaField[SFT], value: SFT
    ) -> ParsedSchemaField:
        return cls(schema_field, value)


@dataclass
class ParsedSchema:
    schema: IdSchemaObject
    id_: str
    fields: list[ParsedSchemaField]
    event_parsed_schema: ParsedSchema | None = None
