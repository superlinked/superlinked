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


from qdrant_client import QdrantClient
from qdrant_client.conversions.common_types import QueryResponse
from qdrant_client.models import SearchParams
from typing_extensions import override

from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_config import (
    VDBKNNSearchConfig,
)
from superlinked.framework.common.storage.search import Search
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.storage.qdrant.qdrant_field_encoder import QdrantFieldEncoder
from superlinked.framework.storage.qdrant.query.qdrant_query import (
    QdrantQuery,
    QdrantQueryBuilder,
)
from superlinked.framework.storage.qdrant.query.qdrant_vdb_knn_search_params import (
    QdrantVDBKNNSearchParams,
)


class QdrantSearch(Search[QdrantVDBKNNSearchParams, QdrantQuery, QueryResponse, VDBKNNSearchConfig]):
    def __init__(self, client: QdrantClient, encoder: QdrantFieldEncoder) -> None:
        super().__init__()
        self._client = client
        self._query_builder = QdrantQueryBuilder(encoder)

    @override
    def build_query(self, search_params: QdrantVDBKNNSearchParams, search_config: VDBKNNSearchConfig) -> QdrantQuery:
        return self._query_builder.build(search_params)

    @override
    async def knn_search(
        self,
        index_config: IndexConfig,
        query: QdrantQuery,
    ) -> QueryResponse:
        is_exact_search = index_config.vector_field_descriptor.search_algorithm == SearchAlgorithm.FLAT
        return self._client.query_points(
            collection_name=query.collection_name,
            query=query.vector.value,
            using=index_config.vector_field_descriptor.field_name,
            query_filter=query.filter_,
            limit=query.limit,
            score_threshold=query.score_treshold,
            search_params=SearchParams(exact=is_exact_search),
            with_vectors=query.with_vector,
            with_payload=query.returned_payload_fields,
        )
