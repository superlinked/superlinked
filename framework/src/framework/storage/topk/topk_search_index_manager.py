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
from typing_extensions import override

from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search_index.manager.search_index_manager import (
    SearchIndexManager,
)
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.storage.topk.topk_field_descriptor_compiler import (
    TopKFieldDescriptorCompiler,
)
from superlinked.framework.storage.topk.topk_vdb_client import TopKVDBClient


class TopKSearchIndexManager(SearchIndexManager):
    def __init__(
        self,
        client: TopKVDBClient,
        index_configs: Sequence[IndexConfig] | None = None,
    ) -> None:
        super().__init__(index_configs)
        self._client = client

    @override
    def _create_search_indices(
        self,
        index_configs: Sequence[IndexConfig],
        collection_name: str,
        override_existing: bool,
    ) -> None:
        collections = self._client.client.collections().list()
        collection = next((collection for collection in collections if collection.name == collection_name), None)
        fields = self._calculate_field_names(index_configs)
        if collection and collection.schema.keys() != fields.keys():
            self._create_search_index(collection_name, fields, override_existing=True)
        elif not collection:
            self._create_search_index(collection_name, fields, override_existing)

    def _calculate_field_names(self, index_configs: Sequence[IndexConfig]) -> dict[str, Any]:
        return {
            k: v
            for index_config in index_configs
            for k, v in TopKFieldDescriptorCompiler.compile_descriptors(index_config.all_field_descriptors)
        }

    def _create_search_index(
        self, collection_name: str, schema: dict[str, Any], override_existing: bool = False
    ) -> None:
        if override_existing:
            self._client.client.collections().delete(collection_name)
        self._client.client.collections().create(
            collection_name,
            schema=schema,
        )

    @property
    @override
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        return [SearchAlgorithm.FLAT]
