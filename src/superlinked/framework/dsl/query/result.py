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

from dataclasses import dataclass
from typing import Any

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.storage.entity import Entity


@dataclass(frozen=True)
class ResultEntry:
    """
    Represents a single entry in a Result, encapsulating the entity and its associated data.

    Attributes:
        entity (Entity): The entity of the result entry.
            This is an instance of the Entity class, which represents a unique entity in the system.
            It contains information such as the entity's ID and type.
        stored_object (dict[str, Any]): The stored object of the result entry.
            This is essentially the raw data that was input into the system.
    """

    entity: Entity
    stored_object: dict[str, Any]


@dataclass(frozen=True)
class Result:
    """
    A class representing the result of a query.

    Attributes:
        schema (IdSchemaObject): The schema of the result.
        entries (list[ResultEntry]): A list of result entries.
    """

    schema: IdSchemaObject
    entries: list[ResultEntry]

    def __str__(self) -> str:
        return "\n".join(
            f"#{i+1} id:{entry.entity.id_.object_id}, object:{entry.stored_object}"
            for i, entry in enumerate(self.entries)
        )
