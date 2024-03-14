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

from typing import cast

from superlinked.framework.common.data_types import Vector
from superlinked.framework.storage.entity import Entity, EntityId
from superlinked.framework.storage.entity_store import EntityStore
from superlinked.framework.storage.field import TextField, VectorField


class EntityStoreManager:
    VECTOR_KEY = "__vector__"
    SCHEMA_NAME_KEY = "__schema__"
    NODE_ID_KEY = "__node_id__"
    OBJECT_ID_KEY = "__object_id__"

    def __init__(self, store: EntityStore) -> None:
        self.store = store

    def set_vector(
        self,
        entity_id: EntityId,
        vector: Vector,
        schema_name: str | None = None,
        origin_id: EntityId | None = None,
    ) -> None:
        self.store.set_field(
            entity_id, EntityStoreManager.VECTOR_KEY, VectorField(vector)
        )
        self._set_entity_base_fields(entity_id, schema_name, origin_id)

    def get_vector(self, entity_id: EntityId) -> Vector | None:
        field = self.store.get_field(entity_id, EntityStoreManager.VECTOR_KEY)
        if not isinstance(field, VectorField):
            raise ValueError(
                f"Field at id ({str(entity_id)}) is not a vector but {type(field)}"
            )
        return field.vector

    def get_entities(self, node_id: str, schema: str) -> list[Entity]:
        filter_fields = {
            EntityStoreManager.NODE_ID_KEY: TextField(node_id),
            EntityStoreManager.SCHEMA_NAME_KEY: TextField(schema),
        }
        return self.store.get_entities(filter_fields)

    def set_property(
        self,
        entity_id: EntityId,
        key: str,
        value: str,
        origin_id: EntityId | None = None,
    ) -> None:
        self.store.set_field(entity_id, key, TextField(value))
        self._set_entity_base_fields(entity_id, origin_id=origin_id)

    def get_property(self, entity_id: EntityId, key: str) -> str | None:
        field = self.store.get_field(entity_id, key)
        if field is None:
            return None
        if not isinstance(field, TextField):
            raise ValueError(f"Field at id ({entity_id}) is not a property.")
        return field.text

    def knn(
        self,
        node_id: str,
        vector: Vector,
        schema_name: str | None = None,
        limit: int | None = None,
        radius: float | None = None,
    ) -> list[Entity]:
        """
        Return K nearest neighbours for the given vector.
        Disclaimer: It returns the item, with the same vector as well.

        :param node_id: ID of the node that produced the vectors that we search in.
        :param vector: Vector to search with.
        :param schema_name: optional schema to limit the vector search space
        :param limit: The maximum number of entities to return. None means no filtering is done.
        :param radius: The maximum distance from the vector for an entity to be returned.
        :return: Entity list ordered by ascending distance.
        """
        filter_fields = {EntityStoreManager.NODE_ID_KEY: TextField(node_id)}
        filter_fields.update(
            {EntityStoreManager.SCHEMA_NAME_KEY: TextField(schema_name)}
            if schema_name
            else {}
        )

        return self.store.knn(
            EntityStoreManager.VECTOR_KEY,
            VectorField(vector),
            filter_fields,
            limit,
            radius,
        )

    def _set_entity_base_fields(
        self,
        entity_id: EntityId,
        schema_name: str | None = None,
        origin_id: EntityId | None = None,
    ) -> None:
        self.store.set_field(
            entity_id, EntityStoreManager.NODE_ID_KEY, TextField(entity_id.node_id)
        )
        self.store.set_field(
            entity_id, EntityStoreManager.OBJECT_ID_KEY, TextField(entity_id.object_id)
        )
        if schema_name is not None:
            self.store.set_field(
                entity_id,
                EntityStoreManager.SCHEMA_NAME_KEY,
                TextField(cast(str, schema_name)),
            )
        if origin_id is not None:
            self.store.set_origin_id(entity_id, origin_id)
