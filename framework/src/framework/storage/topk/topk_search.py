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


import structlog
from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.search import Search
from superlinked.framework.storage.topk.query.topk_query_builder import (
    TopKQueryBuilder,
    VectorQuery,
)
from superlinked.framework.storage.topk.query.vdb_knn_search_params import (
    TopKVDBKNNSearchConfig,
)
from superlinked.framework.storage.topk.topk_field_descriptor_compiler import (
    TopKFieldDescriptorCompiler,
)
from superlinked.framework.storage.topk.topk_field_encoder import TopKFieldEncoder
from superlinked.framework.storage.topk.topk_vdb_client import TopKVDBClient

logger = structlog.get_logger()


class TopKSearch(Search[VDBKNNSearchParams, VectorQuery, list[dict[str, Any]], TopKVDBKNNSearchConfig]):
    def __init__(self, client: TopKVDBClient, encoder: TopKFieldEncoder, collection_name: str) -> None:
        super().__init__()
        self._client = client
        self._query_builder = TopKQueryBuilder(encoder)
        self._collection_name = collection_name

    @override
    def build_query(self, search_params: VDBKNNSearchParams, _: TopKVDBKNNSearchConfig) -> VectorQuery:
        return self._query_builder.build_query(search_params)

    @override
    async def knn_search(
        self,
        index_config: IndexConfig,
        query: VectorQuery,
    ) -> list[dict[str, Any]]:
        docs = self._client.query(self._collection_name, query.topk_query)

        return [
            {TopKFieldDescriptorCompiler._decode_field_name(k): v for k, v in document.items()} for document in docs
        ]
