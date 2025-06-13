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


from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search_index.manager.dynamic_search_index_manager import (
    DynamicSearchIndexManager,
)
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)


class InMemorySearchIndexManager(DynamicSearchIndexManager):
    @property
    @override
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        return [SearchAlgorithm.FLAT]

    @override
    def _list_search_index_names_from_vdb(self, collection_name: str) -> Sequence[str]:
        return list(self._index_configs.keys())

    @override
    def _create_search_index(self, index_config: IndexConfig, collection_name: str) -> None:
        pass

    @override
    def drop_search_index(self, index_name: str, collection_name: str) -> None:
        self._index_configs.pop(index_name, None)
