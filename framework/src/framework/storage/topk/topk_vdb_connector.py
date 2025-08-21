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


from collections import defaultdict

import structlog
from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index.manager.search_index_manager import (
    SearchIndexManager,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.dsl.query.query_user_config import QueryUserConfig
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.topk.query.topk_query_builder import (
    TOPK_VECTOR_DISTANCE_FIELD_NAME,
)
from superlinked.framework.storage.topk.query.vdb_knn_search_params import (
    TopKVDBKNNSearchConfig,
)
from superlinked.framework.storage.topk.topk_connection_params import (
    TopKConnectionParams,
)
from superlinked.framework.storage.topk.topk_field_descriptor_compiler import (
    TOPK_ID_FIELD_NAME,
    TopKFieldDescriptorCompiler,
)
from superlinked.framework.storage.topk.topk_field_encoder import TopKFieldEncoder
from superlinked.framework.storage.topk.topk_search import TopKSearch
from superlinked.framework.storage.topk.topk_search_index_manager import (
    TopKSearchIndexManager,
)
from superlinked.framework.storage.topk.topk_vdb_client import TopKVDBClient

logger = structlog.get_logger()


class TopKVDBConnector(VDBConnector):
    def __init__(self, connection_params: TopKConnectionParams, vdb_settings: VDBSettings) -> None:
        super().__init__(vdb_settings=vdb_settings)
        self._client = TopKVDBClient(connection_params)
        self._encoder = TopKFieldEncoder()
        self.__search_index_manager = TopKSearchIndexManager(self._client)
        self._search = TopKSearch(self._client, self._encoder, self.collection_name)
        self.__vdb_settings = vdb_settings

    @override
    async def close_connection(self) -> None:
        pass  # TopKVDBClient does not require explicit close

    @property
    @override
    def search_index_manager(self) -> SearchIndexManager:
        return self.__search_index_manager

    @property
    @override
    def _default_search_limit(self) -> int:
        return self.__vdb_settings.default_query_limit

    @override
    async def _write_entities(self, entity_data: Sequence[EntityData]) -> None:
        if not entity_data:
            return

        docs = {
            TopKVDBConnector._get_topk_id(ed.id_): {
                TopKFieldDescriptorCompiler._encode_field_name(field_data.name): self._encoder.encode_field(field_data)
                for field_data in ed.field_data.values()
            }
            for ed in entity_data
        }

        self._client.upsert_partial(self.collection_name, docs)

    @override
    async def _read_entities(self, entities: Sequence[Entity]) -> list[EntityData]:
        if not entities:
            return []

        entity_groups = self._group_entities_by_field_keys(entities)

        return [
            entity_data
            for field_keys, grouped_entities in entity_groups.items()
            for entity_data in self._get_entity_group(field_keys, grouped_entities)
        ]

    def _get_entity_group(self, field_keys: tuple[str, ...], entities: list[Entity]) -> list[EntityData]:
        if not entities:
            return []

        ids = [TopKVDBConnector._get_topk_id(entity.id_) for entity in entities]
        documents = self._client.get(self.collection_name, ids, list(field_keys))

        if not documents:
            logger.debug("No documents found for entity group", field_keys=field_keys, ids=ids)
            return []

        return [self._create_entity_data(entity, document) for entity, document in zip(entities, documents.values())]

    def _group_entities_by_field_keys(self, entities: Sequence[Entity]) -> dict[tuple[str, ...], list[Entity]]:
        groups = defaultdict(list)
        for entity in entities:
            field_keys = tuple(sorted(entity.fields.keys()))
            groups[field_keys].append(entity)
        return groups

    def _create_entity_data(self, entity: Entity, document: dict[str, Any]) -> EntityData:
        entity_id = TopKVDBConnector._get_entity_id_from_topk_id(document[TOPK_ID_FIELD_NAME])

        field_data = {}
        for field in entity.fields.values():
            encoded_field_name = TopKFieldDescriptorCompiler._encode_field_name(field.name)
            if encoded_field_name in document and document[encoded_field_name] is not None:
                field_data[field.name] = self._encoder.decode_field(field, document[encoded_field_name])

        return EntityData(entity_id, field_data)

    @override
    async def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        vdb_knn_search_params: VDBKNNSearchParams,
        search_config: TopKVDBKNNSearchConfig,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        index_config = self._get_index_config(index_name)

        result = await self._search.knn_search_with_checks(index_config, vdb_knn_search_params, search_config)

        return [
            ResultEntityData(
                TopKVDBConnector._get_entity_id_from_topk_id(document[TOPK_ID_FIELD_NAME]),
                {
                    returned_field.name: self._encoder.decode_field(returned_field, document[returned_field.name])
                    for returned_field in vdb_knn_search_params.fields_to_return
                    if document.get(returned_field.name) is not None
                },
                float(document[TOPK_VECTOR_DISTANCE_FIELD_NAME]),
            )
            for document in result
        ]

    @override
    def init_search_config(self, query_user_config: QueryUserConfig) -> TopKVDBKNNSearchConfig:
        return TopKVDBKNNSearchConfig()

    @staticmethod
    def _get_topk_id(entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"

    @staticmethod
    def _get_entity_id_from_topk_id(topk_id: str) -> EntityId:
        schema_id, object_id = topk_id.split(":", 1)
        return EntityId(schema_id=schema_id, object_id=object_id)
