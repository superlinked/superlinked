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

from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index.manager.search_index_manager import (
    SearchIndexManager,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.mongo_db.mongo_db_connection_params import (
    MongoDBConnectionParams,
)
from superlinked.framework.storage.mongo_db.mongo_db_field_encoder import (
    MongoDBFieldEncoder,
)
from superlinked.framework.storage.mongo_db.query.mongo_db_query import (
    VECTOR_SCORE_ALIAS,
)
from superlinked.framework.storage.mongo_db.query.mongo_db_search import MongoDBSearch
from superlinked.framework.storage.mongo_db.query.mongo_db_vdb_knn_search_params import (
    MongoDBVDBKNNSearchParams,
)
from superlinked.framework.storage.mongo_db.search_index.mongo_db_search_index_manager import (
    MongoDBSearchIndexManager,
)


class MongoDBVDBConnector(VDBConnector):
    def __init__(self, connection_params: MongoDBConnectionParams, vdb_settings: VDBSettings) -> None:
        super().__init__(vdb_settings=vdb_settings)
        self._client = MongoClient(connection_params.connection_string)
        self._db = self._client[connection_params.db_name]
        self._encoder = MongoDBFieldEncoder()
        self._search_index_manager = MongoDBSearchIndexManager(self._db.name, connection_params.admin_params)
        self._search = MongoDBSearch(self._db, self._encoder)

    @override
    def close_connection(self) -> None:
        # Due to pymongo overwriting __getattr__ and __getitem__
        # type-checkers mistake 'close' for a database.
        self._client.close()  # type: ignore

    @property
    @override
    def search_index_manager(self) -> SearchIndexManager:
        return self._search_index_manager

    @override
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        if not entity_data:
            return
        docs = [
            {
                "_id": MongoDBVDBConnector._get_mongo_id(ed.id_),
                **{field_data.name: self._encoder.encode_field(field_data) for field_data in ed.field_data.values()},
            }
            for ed in entity_data
        ]
        self._db[self.collection_name].bulk_write(
            [UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True) for doc in docs]
        )

    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        if not entities:
            return []

        mongo_ids = [MongoDBVDBConnector._get_mongo_id(entity.id_) for entity in entities]

        docs = {doc["_id"]: doc for doc in self._db[self.collection_name].find({"_id": {"$in": mongo_ids}})}

        return [
            EntityData(
                entity.id_,
                {
                    field.name: self._encoder.decode_field(field, doc.get(field.name))
                    for field in entity.fields.values()
                    if doc.get(field.name) is not None
                },
            )
            for entity in entities
            for doc in [docs.get(MongoDBVDBConnector._get_mongo_id(entity.id_), {})]
        ]

    @override
    def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        index_config = self._get_index_config(index_name)
        results = self._search.knn_search_with_checks(
            index_config,
            MongoDBVDBKNNSearchParams.from_base(
                vdb_knn_search_params,
                self.collection_name,
                index_name,
                params.get("numCandidates"),
            ),
        )
        return [
            ResultEntityData(
                MongoDBVDBConnector._get_entity_id_from_mongo_id(self._encoder._decode_string(document["_id"])),
                self._extract_fields_from_document(document, vdb_knn_search_params.fields_to_return),
                self._encoder._decode_double(document[VECTOR_SCORE_ALIAS]),
            )
            for document in results
        ]

    def _extract_fields_from_document(
        self, document: dict[str, Any], fields_to_return: Sequence[Field]
    ) -> dict[str, FieldData]:
        return {
            returned_field.name: self._encoder.decode_field(returned_field, document[returned_field.name])
            for returned_field in fields_to_return
            if document.get(returned_field.name) is not None
        }

    @staticmethod
    def _get_mongo_id(entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"

    @staticmethod
    def _get_entity_id_from_mongo_id(mongo_id: str) -> EntityId:
        schema_id, object_id = mongo_id.split(":", 1)
        return EntityId(schema_id=schema_id, object_id=object_id)
