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


from beartype.typing import Mapping, Sequence

from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.storage.entity.base_entity import EntityT
from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage_manager.admin_fields import AdminFields


class EntityMerger:
    @classmethod
    def get_unique_entities(cls, entities: Sequence[EntityT]) -> list[EntityT]:
        id_to_entity: dict[EntityId, EntityT] = {}
        for entity in entities:
            existing = id_to_entity.get(entity.id_)
            fields = {**existing.fields, **entity.fields} if existing else entity.fields
            id_to_entity[entity.id_] = type(entity)(entity.id_, fields)
        return list(id_to_entity.values())

    @classmethod
    def build_entity_data_for_original_entities(
        cls, original_entities: Sequence[Entity], id_to_entity_data: Mapping[EntityId, EntityData]
    ) -> list[EntityData]:
        result = []
        for original_entity in original_entities:
            if original_entity.id_ not in id_to_entity_data:
                raise InvalidStateException(
                    "Entity ID not found.",
                    entity_id=original_entity.id_,
                    id_to_entity_data=id_to_entity_data,
                )
            result.append(cls._build_entity_data(original_entity, id_to_entity_data[original_entity.id_]))
        return result

    @classmethod
    def _build_entity_data(cls, original_entity: Entity, entity_data: EntityData) -> EntityData:
        required_fields = set(original_entity.fields.keys()) | set(AdminFields.get_admin_field_names())
        field_data = {
            field_name: field_data
            for field_name, field_data in entity_data.field_data.items()
            if field_name in required_fields
        }
        return EntityData(entity_data.id_, field_data)
