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
from typing import Mapping

from superlinked.framework.storage.field import Field


@dataclass(frozen=True)
class EntityId:
    """
    EntityId is used to identify a single entry within the vector storage.
    """

    object_id: str
    node_id: str
    schema_id: str

    def __str__(self) -> str:
        return f"{self.node_id}:{self.schema_id}:{self.object_id}"


@dataclass
class EntityMetadata:
    """
    EntityMetadata encompasses all possible metadata associated with an entity.
    """

    similarity: float | None


class Entity:
    """
    Entity contains the stored field values of a schema,
    queries return the values in entities too.
    """

    def __init__(
        self,
        id_: EntityId,
        items: Mapping[str, Field],
        origin_id: EntityId | None,
        entity_metadata: EntityMetadata | None,
    ) -> None:
        self.id_ = id_
        self.__items = items
        self.origin_id = origin_id
        self.metadata = entity_metadata or EntityMetadata(None)

    @property
    def _entity_id(self) -> EntityId:
        return self.id_

    @property
    def _items(self) -> Mapping[str, Field]:
        return self.__items

    @property
    def _metadata(self) -> EntityMetadata:
        return self.metadata

    def __getitem__(self, field_name: str) -> Field | None:
        return self.__items.get(field_name)

    def __to_str_dict(self) -> Mapping[str, str]:
        return {key: str(value) for key, value in self.__items.items()}

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, Entity)
            and __value.id_ == self.id_
            and __value.__to_str_dict() == self.__to_str_dict()
            and (__value.origin_id or "") == (self.origin_id or "")
        )

    def __hash__(self) -> int:
        return hash((self.id_, frozenset(self.__to_str_dict()), (self.origin_id or "")))
