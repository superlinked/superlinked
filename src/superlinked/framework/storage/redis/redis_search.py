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
from redis import Redis
from typing_extensions import override

from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.search import Search
from superlinked.framework.storage.redis.query.redis_query_builder import (
    RedisQuery,
    RedisQueryBuilder,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder


class RedisSearch(Search[VDBKNNSearchParams, RedisQuery, dict[bytes, Any]]):
    def __init__(self, client: Redis, encoder: RedisFieldEncoder) -> None:
        super().__init__()
        self._client = client
        self._query_builder = RedisQueryBuilder(encoder)

    @override
    def build_query(
        self, search_params: VDBKNNSearchParams, returned_fields: Sequence[Field]
    ) -> RedisQuery:
        return self._query_builder.build_query(search_params, returned_fields)

    @override
    def knn_search(
        self,
        index_config: IndexConfig,
        query: RedisQuery,
    ) -> dict[bytes, Any]:
        return self._client.ft(index_config.index_name).search(
            query.query, query_params=query.query_params
        )
