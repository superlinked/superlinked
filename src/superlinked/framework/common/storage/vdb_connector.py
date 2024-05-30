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
from typing import Any, Generic

from beartype.typing import Sequence

from superlinked.framework.common.storage.entity import Entity
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.index_config import IndexConfigT
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


class VDBConnector(ABC, Generic[IndexConfigT]):
    def __init__(self, index_configs: Sequence[IndexConfigT] | None = None) -> None:
        self._index_configs: dict[str, IndexConfigT] = {
            index_config.index_name: index_config
            for index_config in (index_configs or [])
        }

    @abstractmethod
    def close_connection(self) -> None:
        pass

    @property
    @abstractmethod
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        pass

    def create_search_index_with_check(
        self,
        index_name: str,
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
        **index_params: Any,
    ) -> None:
        if (
            vector_field_descriptor.search_algorithm
            not in self.supported_vector_indexing
        ):
            raise NotImplementedError(
                f"The specified vector search algorithm {vector_field_descriptor.search_algorithm}"
                + f" is not yet supported. Currently supported algorithms: {self.supported_vector_indexing}"
            )
        return self.create_search_index(
            index_name, vector_field_descriptor, field_descriptors, **index_params
        )

    @abstractmethod
    def create_search_index(
        self,
        index_name: str,
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
        **index_params: Any,
    ) -> None:
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

    @abstractmethod
    def knn_search(
        self,
        index_name: str,
        schema_name: str,
        returned_fields: Sequence[Field],
        vdb_knn_search_params: VDBKNNSearchParams,
        **params: Any,
    ) -> Sequence[ResultEntityData]:
        pass
