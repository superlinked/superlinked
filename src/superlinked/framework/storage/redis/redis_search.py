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


from typing import Any

from beartype.typing import Sequence
from redis import Redis

from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search_mixin import SearchMixin
from superlinked.framework.common.storage.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.storage.redis.query.redis_query_builder import (
    RedisQueryBuilder,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder


class RedisSearch(SearchMixin):
    def __init__(self, client: Redis, encoder: RedisFieldEncoder) -> None:
        self._client = client
        self._encoder = encoder
        self._query_builder = RedisQueryBuilder(self._encoder)

    def knn_search(
        self,
        index_config: IndexConfig,
        returned_fields: Sequence[Field],
        search_params: VDBKNNSearchParams,
    ) -> dict[bytes, Any]:
        self._check_vector_field(index_config, search_params.vector_field)
        self._check_filters(index_config, search_params.filters)
        query = self._query_builder.build_query(search_params, returned_fields)

        return self._client.ft(index_config.index_name).search(
            query.query, query_params=query.query_params
        )
