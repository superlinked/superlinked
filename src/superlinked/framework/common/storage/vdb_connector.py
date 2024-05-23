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
from typing import Any

from beartype.typing import Sequence

from superlinked.framework.common.storage.entity import Entity
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)
from superlinked.framework.common.storage.search_index_creation.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.storage.vdb_knn_search_params import (
    VDBKNNSearchParams,
)


class VDBConnector(ABC):
    @abstractmethod
    def close_connection(self) -> None:
        pass

    @abstractmethod
    def create_search_index(
        self,
        index_name: str,
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
        **index_params: Any
    ) -> None:
        pass

    @abstractmethod
    def drop_search_index(self, index_name: str) -> None:
        pass

    @property
    @abstractmethod
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        pass

    @abstractmethod
    def write_entities(self, entity_data: Sequence[EntityData]) -> None:
        pass

    @abstractmethod
    def read_entities(self, entities: Sequence[Entity]) -> Sequence[EntityData]:
        pass

    @abstractmethod
    def knn_search(
        self,
        index_name: str,
        schema_name: str,
        returned_fields: Sequence[Field],
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any
    ) -> Sequence[ResultEntityData]:
        pass
