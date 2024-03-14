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

from collections import defaultdict
from collections.abc import Mapping
from typing import cast

from superlinked.framework.common.calculation.vector_similarity import (
    SimilarityMethod,
    VectorSimilarityCalculator,
)
from superlinked.framework.storage.entity import Entity, EntityId
from superlinked.framework.storage.entity_store import EntityStore
from superlinked.framework.storage.field import Field, TextField, VectorField


class InMemoryEntityStore(EntityStore):
    """
    Store and retrieve vector and text values.

    Disclaimer: Use this module to test on small number of vectors and vector dimensions.
    It behaves reasonably (<1s) for 10k vectors with 1k dimensions each, when performing KNN.
    """

    ORIGIN_ID_KEY = "__origin_id__"
    ITEMS_KEY = "__items__"
    SIMILARITY_KEY = "__similarity__"

    def __init__(
        self,
        vector_similarity_calculator: VectorSimilarityCalculator = VectorSimilarityCalculator(
            SimilarityMethod.INNER_PRODUCT
        ),
    ) -> None:
        self.entities: defaultdict[str, dict[str, Field]] = defaultdict(lambda: {})
        self.vector_similarity_calculator = vector_similarity_calculator

    def set_field(self, entity_id: EntityId, key: str, value: Field) -> None:
        row_id: str = InMemoryEntityStore._get_row_id_from_entity_id(entity_id)
        entity = self.entities[row_id]
        entity.update({key: value})

    def get_field(self, entity_id: EntityId, key: str) -> Field | None:
        row_id: str = InMemoryEntityStore._get_row_id_from_entity_id(entity_id)
        entity = self.entities[row_id]
        return entity.get(key)

    def set_origin_id(self, entity_id: EntityId, origin_id: EntityId) -> None:
        row_id: str = InMemoryEntityStore._get_row_id_from_entity_id(entity_id)
        entity = self.entities[row_id]
        entity.update(
            {
                InMemoryEntityStore.ORIGIN_ID_KEY: TextField(
                    InMemoryEntityStore._get_row_id_from_entity_id(origin_id)
                )
            }
        )

    def get_origin_id(self, entity_id: EntityId) -> EntityId | None:
        row_id: str = InMemoryEntityStore._get_row_id_from_entity_id(entity_id)
        entity = self.entities[row_id]
        origin_id_field: Field | None = entity.get(InMemoryEntityStore.ORIGIN_ID_KEY)
        if origin_id_field and isinstance(origin_id_field, TextField):
            return InMemoryEntityStore._get_entity_id_from_row_id(origin_id_field.value)
        return None

    def set_entity(self, entity: Entity) -> None:
        row_id: str = InMemoryEntityStore._get_row_id_from_entity_id(entity.id_)
        entity_ = self.entities[row_id]
        entity_.update(entity._items)

    def get_entity(self, entity_id: EntityId) -> Entity:
        row_id: str = InMemoryEntityStore._get_row_id_from_entity_id(entity_id)
        entity = self.entities[row_id]
        origin_id_field: Field | None = entity.get(InMemoryEntityStore.ORIGIN_ID_KEY)
        return Entity(
            entity_id,
            entity,
            (
                InMemoryEntityStore._get_entity_id_from_row_id(origin_id_field.value)
                if origin_id_field
                else None
            ),
            None,
        )

    def get_entities(
        self, key_value_filter: Mapping[str, Field] | None = None
    ) -> list[Entity]:
        return [
            self.get_entity(InMemoryEntityStore._get_entity_id_from_row_id(k))
            for k, v in self.entities.items()
            if InMemoryEntityStore._is_subset(v, key_value_filter)
        ]

    def knn(
        self,
        key: str,
        vector: VectorField,
        key_value_filter: Mapping[str, Field] | None = None,
        limit: int | None = None,
        radius: float | None = None,
    ) -> list[Entity]:
        filtered_entities: dict[str, dict] = {
            k: {InMemoryEntityStore.ITEMS_KEY: v}
            for k, v in self.entities.items()
            if InMemoryEntityStore._is_subset(v, key_value_filter)
        }

        InMemoryEntityStore._validate_entities(filtered_entities, key, vector)

        for k, v in filtered_entities.items():
            actual_vector = cast(VectorField, v[InMemoryEntityStore.ITEMS_KEY][key])
            filtered_entities[k].update(
                {
                    InMemoryEntityStore.SIMILARITY_KEY: self.vector_similarity_calculator.calculate_similarity(
                        actual_vector.value, vector.value
                    )
                }
            )

        sorted_entities = sorted(
            {
                k: v
                for k, v in filtered_entities.items()
                if not radius or v[InMemoryEntityStore.SIMILARITY_KEY] >= (1 - radius)
            }.items(),
            key=lambda x: x[1][InMemoryEntityStore.SIMILARITY_KEY],
            reverse=True,
        )

        return [
            self.__get_entity_with_metadata(row_id, dictionary)
            for row_id, dictionary in (
                sorted_entities[:limit] if limit else sorted_entities
            )
        ]

    def __get_entity_with_metadata(self, row_id: str, entity_dict: dict) -> Entity:
        entity = self.get_entity(InMemoryEntityStore._get_entity_id_from_row_id(row_id))
        entity._metadata.similarity = entity_dict[InMemoryEntityStore.SIMILARITY_KEY]
        return entity

    @staticmethod
    def _is_subset(
        mapping_superset: Mapping[str, Field],
        mapping_subset: Mapping[str, Field] | None = None,
    ) -> bool:
        """
        Return true, if all key,value pairs from `mapping_subset` are present in `mapping_superset`.
        """
        if mapping_subset is None:
            return True

        exploded_mapping_superset = {k: v.value for k, v in mapping_superset.items()}
        exploded_mapping_subset = {k: v.value for k, v in mapping_subset.items()}

        for k, v in exploded_mapping_subset.items():
            if (k, v) not in exploded_mapping_superset.items():
                return False
        return True

    @staticmethod
    def _validate_entities(
        entities: dict[str, dict], key: str, vector: VectorField
    ) -> None:
        for k, v in entities.items():
            items = v[InMemoryEntityStore.ITEMS_KEY]
            if key not in items.keys():
                raise ValueError(f"Entity with id ({k}) does not have field {key}.")
            field = items[key]
            if not isinstance(field, VectorField):
                raise ValueError(
                    f"Field with id ({k}) is not a VectorField, but a {type(items[key])}."
                )
            if field.vector.dimension != vector.vector.dimension:
                raise ValueError(
                    f"VectorField with key ({k}) does not have the same dimensions ({field.vector.dimension}) as the "
                    f"search vector ({vector.vector.dimension})."
                )

    @staticmethod
    def _get_row_id_from_entity_id(entity_id: EntityId) -> str:
        return f"{entity_id.node_id}:{entity_id.schema_id}:{entity_id.object_id}"

    @staticmethod
    def _get_entity_id_from_row_id(row_id: str) -> EntityId:
        node_id, schema_id, object_id = row_id.split(":")
        return EntityId(node_id=node_id, schema_id=schema_id, object_id=object_id)
