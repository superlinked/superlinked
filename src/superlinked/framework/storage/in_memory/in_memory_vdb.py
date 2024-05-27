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

import json
from collections import defaultdict
from typing import Any

from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.calculation.vector_similarity import (
    VectorSimilarityCalculator,
)
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.storage.entity import Entity
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.entity_id import EntityId
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)
from superlinked.framework.common.storage.search_index_creation.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.common.storage.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.storage.in_memory.in_memory_search import InMemorySearch
from superlinked.framework.storage.in_memory.index_config import IndexConfig
from superlinked.framework.storage.in_memory.json_codec import JsonDecoder, JsonEncoder
from superlinked.framework.storage.in_memory.object_serializer import ObjectSerializer


class InMemoryVDB(VDBConnector):
    def __init__(self) -> None:
        super().__init__()
        self._vdb = defaultdict[str, dict[str, Any]](dict)
        self._index_configs: dict[str, IndexConfig] = {}
        self._search = InMemorySearch()

    @override
    def close_connection(self) -> None:
        self._vdb = defaultdict[str, dict[str, Any]](dict)
        self._index_configs = dict[str, IndexConfig]()

    @override
    def create_search_index(
        self,
        index_name: str,
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
        **index_params: Any,
    ) -> None:
        self.drop_search_index(index_name)
        index_config = IndexConfig(
            vector_field_descriptor.field_name,
            [field_descriptor.field_name for field_descriptor in field_descriptors],
            VectorSimilarityCalculator(vector_field_descriptor.distance_metric),
        )
        self._index_configs[index_name] = index_config

    @override
    def drop_search_index(self, index_name: str) -> None:
        self._index_configs.pop(index_name, None)

    @override
    @property
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        return [SearchAlgorithm.FLAT]

    @override
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        for ed in entity_data:
            row_id = InMemoryVDB._get_row_id_from_entity_id(ed.id_)
            self._vdb[row_id].update(
                {name: fd.value for name, fd in ed.field_data.items()}
            )

    @override
    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        return [
            EntityData(
                entity.id_,
                self._find_field_data(
                    InMemoryVDB._get_row_id_from_entity_id(entity.id_),
                    list(entity.fields.values()),
                ),
            )
            for entity in entities
        ]

    def _find_field_data(
        self, row_id: str, fields: Sequence[Field]
    ) -> dict[str, FieldData]:
        raw_entity = self._vdb[row_id]
        return {
            field.name: FieldData.from_field(field, raw_entity.get(field.name))
            for field in fields
            if raw_entity.get(field.name) is not None
        }

    def read_entities_matching_filters(
        self,
        filters: Sequence[ComparisonOperation[Field]],
        has_fields: Sequence[Field],
        return_fields: Sequence[Field],
    ) -> Sequence[EntityData]:
        row_ids = self._search.search(self._vdb, filters, has_fields)
        return [
            EntityData(
                InMemoryVDB._get_entity_id_from_row_id(row_id),
                self._find_field_data(row_id, return_fields),
            )
            for row_id in row_ids
        ]

    @override
    def knn_search(
        self,
        index_name: str,
        schema_name: str,
        returned_fields: Sequence[Field],
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        index_config = self._get_index_config(index_name)
        sorted_scores: list[tuple[str, float]] = self._search.knn_search(
            index_config, self._vdb, vdb_knn_search_params
        )
        return [
            self._get_result_entity_data(row_id, score, returned_fields)
            for row_id, score in sorted_scores
        ]

    def persist(self, serialzer: ObjectSerializer, app_identifier: str) -> None:
        serialzer.write(
            self.__class__.__name__,
            json.dumps(self._vdb, cls=JsonEncoder),
            app_identifier,
        )

    def restore(self, serialzer: ObjectSerializer, app_identifier: str) -> None:
        self._vdb.update(
            json.loads(
                serialzer.read(self.__class__.__name__, app_identifier),
                cls=JsonDecoder,
            )
        )

    def _get_index_config(self, index_name: str) -> IndexConfig:
        index_config = self._index_configs.get(index_name)
        if not index_config:
            raise ValidationException(
                f"Index with the given name {index_name} doesn't exist!"
            )
        return index_config

    def _get_result_entity_data(
        self, row_id: str, score: float, returned_fields: Sequence[Field]
    ) -> ResultEntityData:
        return ResultEntityData(
            InMemoryVDB._get_entity_id_from_row_id(row_id),
            self._find_field_data(row_id, returned_fields),
            score,
        )

    @staticmethod
    def _get_row_id_from_entity_id(entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"

    @staticmethod
    def _get_entity_id_from_row_id(row_id: str) -> EntityId:
        schema_id, object_id = row_id.split(":")
        return EntityId(schema_id=schema_id, object_id=object_id)