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
from superlinked.framework.common.storage.field_data import VectorField
from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
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
    def supported_vector_indexing(self) -> Sequence[Any]:
        pass

    @abstractmethod
    def knn_search(
        self,
        index_name: str,
        schema: str,
        vector_field: VectorField,
        returned_fields: Sequence[Field],
        limit: int,
        **params: Any
    ) -> Any:
        pass

    @abstractmethod
    def write_fields(self, fields: Sequence[EntityData]) -> None:
        pass

    @abstractmethod
    def read_field(self, fields: Sequence[Entity]) -> Sequence[EntityData]:
        pass
