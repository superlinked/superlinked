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

from abc import ABC, abstractmethod
from collections.abc import Mapping

from superlinked.framework.storage.entity import Entity, EntityId
from superlinked.framework.storage.field import Field, VectorField


class EntityStore(ABC):
    """
    Interface for vector databases that can store and filter by key-value pairs.
    """

    @abstractmethod
    def set_field(self, entity_id: EntityId, key: str, value: Field) -> None:
        pass

    @abstractmethod
    def get_field(self, entity_id: EntityId, key: str) -> Field | None:
        pass

    @abstractmethod
    def set_origin_id(self, entity_id: EntityId, origin_id: EntityId) -> None:
        pass

    @abstractmethod
    def get_origin_id(self, entity_id: EntityId) -> EntityId | None:
        pass

    @abstractmethod
    def set_entity(self, entity: Entity) -> None:
        pass

    @abstractmethod
    def get_entity(self, entity_id: EntityId) -> Entity:
        pass

    @abstractmethod
    def get_entities(
        self, key_value_filter: Mapping[str, Field] | None
    ) -> list[Entity]:
        pass

    @abstractmethod
    def knn(
        self,
        key: str,
        vector: VectorField,
        key_value_filter: Mapping[str, Field] | None,
        limit: int | None,
        radius: float | None,
    ) -> list[Entity]:
        pass
