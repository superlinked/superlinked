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

from beartype.typing import Sequence

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)


class SearchIndexManager(ABC):
    def __init__(self, index_configs: Sequence[IndexConfig] | None = None) -> None:
        self._index_configs = {index_config.index_name: index_config for index_config in index_configs or []}

    @property
    @abstractmethod
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        pass

    def init_search_indices(
        self,
        index_configs: Sequence[IndexConfig],
        collection_name: str,
        create_search_indices: bool,
        override_existing: bool = False,
    ) -> None:
        self._index_configs.clear()
        if create_search_indices:
            self._create_search_indices(index_configs, collection_name, override_existing)
        self._index_configs.update({index_config.index_name: index_config for index_config in index_configs})

    @abstractmethod
    def _create_search_indices(
        self,
        index_configs: Sequence[IndexConfig],
        collection_name: str,
        override_existing: bool,
    ) -> None:
        pass

    def get_index_config(self, index_name: str) -> IndexConfig:
        index_config = self._index_configs.get(index_name)
        if not index_config:
            raise InvalidInputException(f"Index with the given name {index_name} doesn't exist.")
        return index_config

    def clear_configs(self) -> None:
        self._index_configs.clear()
