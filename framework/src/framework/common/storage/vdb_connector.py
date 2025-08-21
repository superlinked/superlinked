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

from abc import ABC, abstractmethod

from beartype.typing import Any, Generic, Sequence, TypeVar

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.precision import Precision
from superlinked.framework.common.settings import settings
from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.entity.entity_merger import EntityMerger
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_config import (
    VDBKNNSearchConfig,
)
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index.manager.search_index_manager import (
    SearchIndexManager,
)
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.telemetry.telemetry_registry import (
    TelemetryAttributeType,
    telemetry,
)
from superlinked.framework.dsl.query.query_user_config import QueryUserConfig
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.in_memory.object_serializer import ObjectSerializer

VDBKNNSearchConfigT = TypeVar("VDBKNNSearchConfigT", bound=VDBKNNSearchConfig)


class VDBConnector(ABC, Generic[VDBKNNSearchConfigT]):
    def __init__(self, vdb_settings: VDBSettings, index_configs: Sequence[IndexConfig] | None = None) -> None:
        self.__vdb_settings = vdb_settings
        self._index_configs: dict[str, IndexConfig] = {
            index_config.index_name: index_config for index_config in (index_configs or [])
        }
        self._app_id = settings.APP_ID

    @property
    def distance_metric(self) -> DistanceMetric:
        return self.__vdb_settings.distance_metric

    @property
    def search_algorithm(self) -> SearchAlgorithm:
        return self.__vdb_settings.search_algorithm

    @property
    def _default_search_limit(self) -> int:
        return self.__vdb_settings.default_query_limit

    @property
    def vector_precision(self) -> Precision:
        return self.__vdb_settings.vector_precision

    @property
    def collection_name(self) -> str:
        if self._app_id is None:
            raise InvalidStateException(
                "app id wasn't initialized properly "
                + "by either initializing the vdb connector with a set of index configs "
                + "or calling init_search_index_configs with them."
            )
        return self._app_id

    @abstractmethod
    async def close_connection(self) -> None:
        pass

    @property
    @abstractmethod
    def search_index_manager(self) -> SearchIndexManager:
        pass

    def persist(self, _: ObjectSerializer) -> None:
        """
        Persist the state of the VDB. Implement this method in subclasses if persistence is supported.
        """

    def restore(self, _: ObjectSerializer) -> None:
        """
        Restore the state of the VDB. Implement this method in subclasses if restoration is supported.
        """

    def init_search_index_configs(
        self,
        index_configs: Sequence[IndexConfig],
        create_search_indices: bool,
        override_existing: bool = False,
    ) -> None:
        self.search_index_manager.init_search_indices(
            index_configs,
            self.collection_name,
            create_search_indices,
            override_existing,
        )

    async def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        labels: dict[str, TelemetryAttributeType] = {
            "entity_data_count": len(entity_data),
            "vdb_type": type(self).__name__,
        }
        telemetry.record_metric("vdb.write.count", 1, labels)
        unique_entity_data_items = EntityMerger.get_unique_entities(entity_data)
        return await self._write_entities(unique_entity_data_items)

    async def read_entities(self, entities: Sequence[Entity]) -> list[EntityData]:
        labels: dict[str, TelemetryAttributeType] = {"entity_count": len(entities), "vdb_type": type(self).__name__}
        telemetry.record_metric("vdb.read.count", 1, labels)
        unique_entities = EntityMerger.get_unique_entities(entities)
        unique_entity_data = await self._read_entities(unique_entities)
        entity_data_map: dict[EntityId, EntityData] = {
            entity_data.id_: entity_data for entity_data in unique_entity_data
        }
        return EntityMerger.build_entity_data_for_original_entities(entities, entity_data_map)

    @abstractmethod
    async def _write_entities(self, entity_data: Sequence[EntityData]) -> None:
        pass

    @abstractmethod
    async def _read_entities(self, entities: Sequence[Entity]) -> list[EntityData]:
        pass

    async def knn_search(
        self,
        index_name: str,
        schema_name: str,
        vdb_knn_search_params: VDBKNNSearchParams,
        search_config: VDBKNNSearchConfigT,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        # If the limit is set to the default, assign it a database-specific default value
        limit = (
            self._default_search_limit
            if vdb_knn_search_params.limit == constants.DEFAULT_LIMIT
            else vdb_knn_search_params.limit
        )
        search_params = VDBKNNSearchParams(
            vector_field=vdb_knn_search_params.vector_field,
            limit=limit,
            fields_to_return=vdb_knn_search_params.fields_to_return,
            filters=vdb_knn_search_params.filters,
            radius=vdb_knn_search_params.radius,
        )
        labels = {
            "index_name": index_name,
            "schema_name": schema_name,
            "distance_metric": self.distance_metric.value,
            "search_algorithm": self.search_algorithm.value,
            "vector_precision": self.vector_precision.value,
            "limit": search_params.limit,
            "radius": search_params.radius,
        }
        telemetry.record_metric("vdb.knn.count", 1, labels)
        return await self._knn_search(index_name, schema_name, search_params, search_config, **params)

    @abstractmethod
    async def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        vdb_knn_search_params: VDBKNNSearchParams,
        search_config: VDBKNNSearchConfigT,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        pass

    @abstractmethod
    def init_search_config(self, query_user_config: QueryUserConfig) -> VDBKNNSearchConfigT:
        pass

    def _get_index_config(self, index_name: str) -> IndexConfig:
        return self.search_index_manager.get_index_config(index_name)
