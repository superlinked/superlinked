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
import re

from beartype.typing import Any, Sequence, cast
from qdrant_client import QdrantClient
from qdrant_client.conversions.common_types import Payload, Record
from qdrant_client.http.models.models import QueryResponse, ScoredPoint
from qdrant_client.models import (
    PointsList,
    PointStruct,
    PointVectors,
    SetPayload,
    SetPayloadOperation,
    UpdateOperation,
    UpdateVectors,
    UpdateVectorsOperation,
    UpsertOperation,
    VectorStruct,
)
from typing_extensions import override

from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.exception import IndexConfigNotFoundException
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index.manager.search_index_manager import (
    SearchIndexManager,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.common.util.string_util import StringUtil
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.qdrant.qdrant_connection_params import (
    QdrantConnectionParams,
)
from superlinked.framework.storage.qdrant.qdrant_field_encoder import (
    QdrantEncodedTypes,
    QdrantFieldEncoder,
)
from superlinked.framework.storage.qdrant.qdrant_search_index_manager import (
    QdrantSearchIndexManager,
)
from superlinked.framework.storage.qdrant.query.qdrant_search import QdrantSearch
from superlinked.framework.storage.qdrant.query.qdrant_vdb_knn_search_params import (
    QdrantVDBKNNSearchParams,
)

ID_PAYLOAD_FIELD_NAME = "__original_entity_id__"
ID_PAYLOAD_FIELD = Field(FieldDataType.STRING, ID_PAYLOAD_FIELD_NAME)


class QdrantVDBConnector(VDBConnector):
    def __init__(self, connection_params: QdrantConnectionParams, vdb_settings: VDBSettings) -> None:
        super().__init__(vdb_settings=vdb_settings)
        self._client = QdrantClient(
            url=connection_params.connection_string,
            api_key=connection_params._api_key,
            timeout=connection_params.timeout,
            prefer_grpc=connection_params.prefer_grpc,
        )
        self._encoder = QdrantFieldEncoder()
        self.__search_index_manager = QdrantSearchIndexManager(self._client)
        self._search = QdrantSearch(self._client, self._encoder)
        self._vector_field_names = list[str]()

    @override
    def close_connection(self) -> None:
        self._client.close()

    @property
    @override
    def search_index_manager(self) -> SearchIndexManager:
        return self.__search_index_manager

    @override
    def init_search_index_configs(
        self,
        index_configs: Sequence[IndexConfig],
        create_search_indices: bool,
        override_existing: bool = False,
    ) -> None:
        super().init_search_index_configs(index_configs, create_search_indices, override_existing)
        self._vector_field_names.extend(
            [index_config.vector_field_descriptor.field_name for index_config in index_configs]
        )

    @override
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        if not self.search_index_manager._index_configs:
            raise IndexConfigNotFoundException(
                f"{type(self).__name__} can work properly only after initializing " + "the search indices."
            )
        points = [
            PointStruct(
                id=QdrantVDBConnector._get_qdrant_id(ed.id_),
                vector=cast(VectorStruct, self._get_point_vector_dict(ed)),
                payload=self._get_point_payload_dict(ed),
            )
            for ed in entity_data
        ]
        non_existing_points, existing_points = self._split_points_by_existing(points)
        update_operations = list[UpdateOperation]()
        if non_existing_points:
            update_operations.append(UpsertOperation(upsert=PointsList(points=list(non_existing_points))))
        update_vectors_points = [
            PointVectors(id=point.id, vector=point.vector) for point in existing_points if point.vector
        ]
        if update_vectors_points:
            update_operations.append(UpdateVectorsOperation(update_vectors=UpdateVectors(points=update_vectors_points)))
        set_payload_operations = [
            SetPayloadOperation(set_payload=SetPayload(payload=point.payload, points=[point.id]))
            for point in existing_points
            if point.payload
        ]
        if set_payload_operations:
            update_operations.extend(set_payload_operations)
        self._client.batch_update_points(self.collection_name, update_operations=update_operations)

    def _get_point_vector_dict(self, entity_data: EntityData) -> dict[str, QdrantEncodedTypes]:
        return {
            field_data.name: self._encoder.encode_field(field_data)
            for field_data in entity_data.field_data.values()
            if field_data.name in self._vector_field_names
        }

    def _get_point_payload_dict(self, entity_data: EntityData) -> dict[str, QdrantEncodedTypes]:
        field_data: list[FieldData] = list(entity_data.field_data.values()) + [
            FieldData.from_field(
                ID_PAYLOAD_FIELD,
                QdrantVDBConnector._entity_id_to_payload(entity_data.id_),
            )
        ]
        return {
            field_data.name: self._encoder.encode_field(field_data)
            for field_data in field_data
            if field_data.name not in self._vector_field_names
        }

    def _split_points_by_existing(
        self, points: Sequence[PointStruct]
    ) -> tuple[Sequence[PointStruct], Sequence[PointStruct]]:
        existing_point_records = self._client.retrieve(
            self.collection_name, [point.id for point in points], with_payload=False
        )
        existing_point_ids = [point.id for point in existing_point_records]
        non_existing_points = [point for point in points if point.id not in existing_point_ids]
        existing_points = [point for point in points if point.id in existing_point_ids]
        return non_existing_points, existing_points

    @override
    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        returned_field_names = {field.name for entity in entities for field in entity.fields.values()} | {
            ID_PAYLOAD_FIELD_NAME
        }
        vector_fields = list(
            {field_name for field_name in returned_field_names if field_name in self._vector_field_names}
        )
        payload_fields = list(
            {
                self.sanitize_field_name(field_name)
                for field_name in returned_field_names
                if field_name not in vector_fields
            }
        )
        points = self._client.retrieve(
            self.collection_name,
            ids=[QdrantVDBConnector._get_qdrant_id(entity.id_) for entity in entities],
            with_vectors=vector_fields or False,
            with_payload=payload_fields or False,
        )
        points_by_entity_id = {
            self._entity_id_from_payload(payload): point
            for point in points
            if (payload := self._check_and_get_payload(point))
        }
        return [self._get_entity_data_from_point(entity, points_by_entity_id.get(entity.id_)) for entity in entities]

    def _get_entity_data_from_point(self, entity: Entity, point: Record | None) -> EntityData:
        if point is None:
            return EntityData(entity.id_, {})
        payload_fields = self._check_and_get_payload(point)
        vector_fields = self._check_and_get_vectors(point)
        all_fields_to_return = payload_fields | vector_fields
        return EntityData(
            entity.id_,
            {
                field.name: self._encoder.decode_field(field, field_value)
                for field, field_value in [
                    (field, all_fields_to_return.get(field.name)) for field in entity.fields.values()
                ]
                if field_value is not None
            },
        )

    @override
    def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        index_config = self._get_index_config(index_name)
        extended_fields_to_return = list(vdb_knn_search_params.fields_to_return) + [ID_PAYLOAD_FIELD]
        result: QueryResponse = self._search.knn_search_with_checks(
            index_config,
            QdrantVDBKNNSearchParams.from_base(vdb_knn_search_params, self.collection_name, extended_fields_to_return),
        )
        return [
            self._get_result_entity_data_from_point(point, vdb_knn_search_params.fields_to_return)
            for point in self._calculate_sorted_result_points(result.points)
        ]

    def _calculate_sorted_result_points(self, scored_points: Sequence[ScoredPoint]) -> list[ScoredPoint]:
        """Sort by score descending, then by id ascending"""
        result_points = list(scored_points)
        result_points.sort(
            key=lambda point: (
                -point.score,
                point.payload.get(ID_PAYLOAD_FIELD_NAME) if point.payload else None,
            )
        )
        return result_points

    def _get_result_entity_data_from_point(
        self, point: ScoredPoint, fields_to_return: Sequence[Field]
    ) -> ResultEntityData:
        payload_fields = self._check_and_get_payload(point)
        vector_fields = self._check_and_get_vectors(point)
        all_fields_to_return = payload_fields | vector_fields
        id_ = self._entity_id_from_payload(payload_fields)
        return ResultEntityData(
            id_,
            {
                field.name: self._encoder.decode_field(field, all_fields_to_return[field.name])
                for field in fields_to_return
                if all_fields_to_return.get(field.name) is not None
            },
            self._encoder._decode_base_type(point.score),
        )

    def _check_and_get_vectors(self, point: Record | ScoredPoint) -> dict[str, list[float]]:
        if point.vector is None:
            return {}
        if not isinstance(point.vector, dict) or any(v for v in point.vector.values() if not isinstance(v, list)):
            raise ValueError(f"Retrieved point's payload is invalid: {[point.payload]}")
        return cast(dict[str, list[float]], point.vector)

    def _check_and_get_payload(self, point: Record | ScoredPoint) -> dict[str, Any]:
        if point.payload is None or not isinstance(point.payload, dict):
            raise ValueError(f"Retrieved point's payload is invalid: {[point.payload]}")
        return cast(dict[str, Any], point.payload)

    @staticmethod
    def _get_qdrant_id(entity_id: EntityId) -> str:
        return StringUtil.deterministic_hash_of_strings([entity_id.schema_id, entity_id.object_id])

    @staticmethod
    def _entity_id_to_payload(entity_id: EntityId) -> str:
        return f"{entity_id.schema_id}:{entity_id.object_id}"

    def _entity_id_from_payload(self, payload: Payload) -> EntityId:
        id_str = payload.get(ID_PAYLOAD_FIELD_NAME)
        if id_str is None or not isinstance(id_str, str):
            raise ValueError(f"The mandatory {ID_PAYLOAD_FIELD_NAME} is invalid: {id_str}.")
        schema_id, object_id = self._encoder._decode_base_type(id_str).split(":", 1)
        return EntityId(schema_id=schema_id, object_id=object_id)

    @staticmethod
    def sanitize_field_name(field_name: str) -> str:
        return re.sub(r"[^A-Za-z0-9_]", "_", field_name)
