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

import redis
from beartype.typing import Any, Sequence, cast
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from typing_extensions import override

from superlinked.framework.common.storage.entity import Entity
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.entity_id import EntityId
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index_creation.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.redis.query.redis_query_builder import (
    VECTOR_SCORE_ALIAS,
)
from superlinked.framework.storage.redis.redis_connection_params import (
    RedisConnectionParams,
)
from superlinked.framework.storage.redis.redis_field_descriptor_compiler import (
    RedisFieldDescriptorCompiler,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder
from superlinked.framework.storage.redis.redis_search import RedisSearch


class RedisVDBConnector(VDBConnector):
    def __init__(
        self, connection_params: RedisConnectionParams, vdb_settings: VDBSettings
    ) -> None:
        super().__init__()
        self._client = redis.from_url(connection_params.connection_string, protocol=3)
        self._encoder = RedisFieldEncoder()
        self._search = RedisSearch(self._client, self._encoder)
        self.__vdb_settings = vdb_settings

    @override
    def close_connection(self) -> None:
        self._client.close()

    @override
    @property
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        return [SearchAlgorithm.FLAT, SearchAlgorithm.HNSW]

    @override
    @property
    def _default_search_limit(self) -> int:
        return self.__vdb_settings.default_query_limit

    @override
    def _list_search_index_names_from_vdb(self) -> Sequence[str]:
        return list(
            self._encoder._decode_string(cast(bytes, index_name))
            for index_name in self._client.execute_command("FT._LIST")
        )

    @override
    def create_search_index(self, index_config: IndexConfig) -> None:
        index_def = IndexDefinition(index_type=IndexType.HASH)
        fields = RedisFieldDescriptorCompiler.compile_descriptors(
            index_config.vector_field_descriptor, index_config.field_descriptors
        )
        self._client.ft(index_config.index_name).create_index(
            fields, definition=index_def
        )

    @override
    def drop_search_index(self, index_name: str) -> None:
        self._client.ft(index_name).dropindex()
        self._index_configs.pop(index_name, None)

    @override
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        if entity_data:
            _pipeline = self._client.pipeline(transaction=False)
            for ed in entity_data:
                if ed.field_data:
                    _pipeline.hset(
                        RedisVDBConnector._get_redis_id(ed.id_),
                        mapping={
                            field_name: self._encoder.encode_field(field)
                            for field_name, field in ed.field_data.items()
                        },
                    )
            _pipeline.execute()

    def _read_entity(self, entity: Entity) -> EntityData:
        encoded_field_values = self._client.hmget(
            RedisVDBConnector._get_redis_id(entity.id_),
            [field.name for field in entity.fields.values()],
        )
        return EntityData(
            entity.id_,
            {
                field.name: self._encoder.decode_field(field, encoded_field_values[i])
                for i, field in enumerate(entity.fields.values())
                if encoded_field_values[i] is not None
            },
        )

    @override
    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        return [self._read_entity(entity) for entity in entities if entity.fields]

    @override
    def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        returned_fields: Sequence[Field],
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        index_config = self._get_index_config(index_name)
        result = self._encoder.convert_bytes_keys(
            self._search.knn_search_with_checks(
                index_config, returned_fields, vdb_knn_search_params
            )
        )
        return [
            ResultEntityData(
                RedisVDBConnector._get_entity_id_from_redis_id(
                    self._encoder._decode_string(document["id"])
                ),
                self._extract_fields_from_document(
                    document["extra_attributes"], returned_fields
                ),
                self._encoder._decode_double(
                    document["extra_attributes"][VECTOR_SCORE_ALIAS]
                ),
            )
            for document in result["results"]
        ]

    def _extract_fields_from_document(
        self, document: dict[str, Any], returned_fields: Sequence[Field]
    ) -> dict[str, FieldData]:
        return {
            returned_field.name: self._encoder.decode_field(
                returned_field, document[returned_field.name]
            )
            for returned_field in returned_fields
            if document.get(returned_field.name) is not None
        }

    @staticmethod
    def _get_redis_id(entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"

    @staticmethod
    def _get_entity_id_from_redis_id(redis_id: str) -> EntityId:
        schema_id, object_id = redis_id.split(":", 1)
        return EntityId(schema_id=schema_id, object_id=object_id)
