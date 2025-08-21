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

import structlog
from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
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
from superlinked.framework.storage.redis.query.vdb_knn_search_params import (
    RedisVDBKNNSearchConfig,
)
from superlinked.framework.storage.redis.redis_connection_params import (
    RedisConnectionParams,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder
from superlinked.framework.storage.redis.redis_search import RedisSearch
from superlinked.framework.storage.redis.redis_search_index_manager import (
    RedisSearchIndexManager,
)
from superlinked.framework.storage.redis.redis_vdb_client import RedisVDBClient

logger = structlog.getLogger()


class RedisVDBConnector(VDBConnector[RedisVDBKNNSearchConfig]):
    def __init__(
        self,
        connection_params: RedisConnectionParams,
        vdb_settings: VDBSettings,
    ) -> None:
        super().__init__(vdb_settings=vdb_settings)
        self._client = RedisVDBClient(connection_params.connection_string)
        self._encoder = RedisFieldEncoder(self.vector_precision)
        self.__search_index_manager = RedisSearchIndexManager(self._client, self._encoder)
        self._search = RedisSearch(self._client, self._encoder, self.vector_precision)

    @override
    async def close_connection(self) -> None:
        await self._client.client.close()

    @property
    @override
    def search_index_manager(self) -> SearchIndexManager:
        return self.__search_index_manager

    @override
    async def _write_entities(self, entity_data: Sequence[EntityData]) -> None:
        if entity_data:
            _pipeline = self._client.client.pipeline(transaction=False)
            for ed in entity_data:
                if ed.field_data:
                    _pipeline.hset(
                        self._encoder.encode_entity_id_to_redis_id(ed.id_),
                        mapping={
                            field_name: self._encoder.encode_field(field) for field_name, field in ed.field_data.items()
                        },
                    )
            await _pipeline.execute()

    @override
    async def _read_entities(self, entities: Sequence[Entity]) -> list[EntityData]:
        valid_entities = [entity for entity in entities if entity.fields]
        if not valid_entities:
            return []

        pipeline = self._client.client.pipeline(transaction=False)

        for entity in valid_entities:
            pipeline.hmget(
                self._encoder.encode_entity_id_to_redis_id(entity.id_),
                [field.name for field in entity.fields.values()],
            )

        all_encoded_values = await pipeline.execute()

        return [
            EntityData(
                entity.id_,
                {
                    field.name: self._encoder.decode_field(field, encoded_values[i])
                    for i, field in enumerate(entity.fields.values())
                    if encoded_values[i] is not None
                },
            )
            for entity, encoded_values in zip(valid_entities, all_encoded_values)
        ]

    @override
    async def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        vdb_knn_search_params: VDBKNNSearchParams,
        search_config: RedisVDBKNNSearchConfig,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        index_config = self._get_index_config(index_name)
        results = await self._search.knn_search_with_checks(index_config, vdb_knn_search_params, search_config)
        return [
            ResultEntityData(
                id_=result.entity_id,
                fields={
                    field.name: (self._encoder.decode_field(field, result.field_name_to_data[field.name]))
                    for field in vdb_knn_search_params.fields_to_return
                },
                score=result.score,
            )
            for result in results
        ]

    @override
    def init_search_config(self, query_user_config: QueryUserConfig) -> RedisVDBKNNSearchConfig:
        return RedisVDBKNNSearchConfig(query_user_config.redis_hybrid_policy, query_user_config.redis_batch_size)
