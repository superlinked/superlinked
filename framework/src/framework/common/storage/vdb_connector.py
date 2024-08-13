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

from beartype.typing import Any, Sequence

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.storage.entity import Entity
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index_creation.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.storage.search_index_creation.vector_component_precision import (
    VectorComponentPrecision,
)
from superlinked.framework.storage.in_memory.object_serializer import ObjectSerializer


class VDBConnector(ABC):
    def __init__(
        self,
        distance_metric: DistanceMetric = DistanceMetric.INNER_PRODUCT,
        search_algorithm: SearchAlgorithm = SearchAlgorithm.FLAT,
        vector_coordinate_type: VectorComponentPrecision = VectorComponentPrecision.FLOAT32,
        index_configs: Sequence[IndexConfig] | None = None,
    ) -> None:
        self._distance_metric = distance_metric
        self._search_algorithm = search_algorithm
        self._vector_coordinate_type = vector_coordinate_type
        self._index_configs: dict[str, IndexConfig] = {
            index_config.index_name: index_config
            for index_config in (index_configs or [])
        }

    @property
    def distance_metric(self) -> DistanceMetric:
        return self._distance_metric

    @property
    def search_algorithm(self) -> SearchAlgorithm:
        return self._search_algorithm

    @property
    def vector_coordinate_type(self) -> VectorComponentPrecision:
        return self._vector_coordinate_type

    @abstractmethod
    def close_connection(self) -> None:
        pass

    @property
    @abstractmethod
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        pass

    @property
    @abstractmethod
    def _default_search_limit(self) -> int:
        pass

    @abstractmethod
    def _list_search_index_names_from_vdb(self) -> Sequence[str]:
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
        override_existing: bool = False,
    ) -> None:
        existing_index_names = self._list_search_index_names_from_vdb()
        for index_config in index_configs:
            if index_config.index_name not in existing_index_names or override_existing:
                self.create_search_index_with_check(index_config)
            else:
                self._index_configs[index_config.index_name] = index_config

    def create_search_index_with_check(self, index_config: IndexConfig) -> None:
        if index_config.index_name not in self._index_configs.keys():
            if (
                index_config.vector_field_descriptor.search_algorithm
                not in self.supported_vector_indexing
            ):
                raise NotImplementedError(
                    f"The specified vector search algorithm {index_config.vector_field_descriptor.search_algorithm}"
                    + f" is not yet supported. Currently supported algorithms: {self.supported_vector_indexing}"
                )
            self.create_search_index(index_config)
            self._index_configs[index_config.index_name] = index_config

    @abstractmethod
    def create_search_index(self, index_config: IndexConfig) -> None:
        pass

    @abstractmethod
    def drop_search_index(self, index_name: str) -> None:
        pass

    @abstractmethod
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        pass

    @abstractmethod
    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        pass

    def knn_search(
        self,
        index_name: str,
        schema_name: str,
        returned_fields: Sequence[Field],
        vdb_knn_search_params: VDBKNNSearchParams,
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
            filters=vdb_knn_search_params.filters,
            radius=vdb_knn_search_params.radius,
        )
        return self._knn_search(
            index_name, schema_name, returned_fields, search_params, **params
        )

    @abstractmethod
    def _knn_search(
        self,
        index_name: str,
        schema_name: str,
        returned_fields: Sequence[Field],
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        pass

    def _get_index_config(self, index_name: str) -> IndexConfig:
        index_config = self._index_configs.get(index_name)
        if not index_config:
            raise ValidationException(
                f"Index with the given name {index_name} doesn't exist!"
            )
        return index_config
