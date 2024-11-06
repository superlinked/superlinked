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

from beartype.typing import Any, Sequence
from pymongo import MongoClient, UpdateOne
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
from superlinked.framework.storage.mongo.mongo_connection_params import (
    MongoConnectionParams,
)
from superlinked.framework.storage.mongo.mongo_field_encoder import MongoFieldEncoder
from superlinked.framework.storage.mongo.query.mongo_query import VECTOR_SCORE_ALIAS
from superlinked.framework.storage.mongo.query.mongo_search import MongoSearch
from superlinked.framework.storage.mongo.query.mongo_vdb_knn_search_params import (
    MongoVDBKNNSearchParams,
)
from superlinked.framework.storage.mongo.search_index.mongo_search_index_manager import (
    MongoSearchIndexManager,
)

GENERAL_COLLECTION_NAME = "general_collection"


class MongoVDBConnector(VDBConnector):
    def __init__(
        self, connection_params: MongoConnectionParams, vdb_settings: VDBSettings
    ) -> None:
        super().__init__()
        self._client = MongoClient(connection_params.connection_string)
        self._db = self._client[connection_params.db_name]
        self._collection_name = GENERAL_COLLECTION_NAME
        self._encoder = MongoFieldEncoder()
        self._search_index_manager = MongoSearchIndexManager(
            connection_params.admin_params
        )
        self._search = MongoSearch(self._db[self._collection_name], self._encoder)
        self.__vdb_settings = vdb_settings

    @override
    def close_connection(self) -> None:
        # Due to pymongo overwriting __getattr__ and __getitem__
        # type-checkers mistake 'close' for a database.
        self._client.close()  # type: ignore

    @property
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        return [SearchAlgorithm.FLAT]

    @property
    @override
    def _default_search_limit(self) -> int:
        return self.__vdb_settings.default_query_limit

    @override
    def _list_search_index_names_from_vdb(self) -> Sequence[str]:
        return list(
            self._search_index_manager.get_search_index_ids_by_name(
                self._db.name, self._collection_name
            ).keys()
        )

    @override
    def create_search_index(self, index_config: IndexConfig) -> None:
        self._search_index_manager.create_search_index(
            self._db.name,
            self._collection_name,
            index_config.index_name,
            index_config.vector_field_descriptor,
            index_config.field_descriptors,
        )

    @override
    def drop_search_index(self, index_name: str) -> None:
        self._search_index_manager.drop_search_index(
            self._db.name, self._collection_name, index_name
        )
        self._index_configs.pop(index_name, None)

    @override
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        if not entity_data:
            return
        docs = [
            {
                "_id": MongoVDBConnector._get_mongo_id(ed.id_),
                **{
                    field_data.name: self._encoder.encode_field(field_data)
                    for field_data in ed.field_data.values()
                },
            }
            for ed in entity_data
        ]
        self._db[self._collection_name].bulk_write(
            [UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True) for doc in docs]
        )

    def _read_field_data(self, entity: Entity) -> dict[str, FieldData]:
        doc = (
            self._db[self._collection_name].find_one(
                {"_id": MongoVDBConnector._get_mongo_id(entity.id_)}
            )
            or {}
        )
        return {
            field.name: self._encoder.decode_field(field, doc[field.name])
            for field in entity.fields.values()
            if doc.get(field.name) is not None
        }

    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        return [
            EntityData(
                entity.id_,
                self._read_field_data(entity),
            )
            for entity in entities
        ]

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
        results = self._search.knn_search_with_checks(
            index_config,
            returned_fields,
            MongoVDBKNNSearchParams.from_base(
                vdb_knn_search_params,
                index_name,
                params.get("numCandidates"),
            ),
        )
        return [
            ResultEntityData(
                MongoVDBConnector._get_entity_id_from_mongo_id(
                    self._encoder._decode_string(document["_id"])
                ),
                self._extract_fields_from_document(document, returned_fields),
                self._encoder._decode_double(document[VECTOR_SCORE_ALIAS]),
            )
            for document in results
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
    def _get_mongo_id(entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"

    @staticmethod
    def _get_entity_id_from_mongo_id(mongo_id: str) -> EntityId:
        schema_id, object_id = mongo_id.split(":", 1)
        return EntityId(schema_id=schema_id, object_id=object_id)
