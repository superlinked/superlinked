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

from dataclasses import asdict

from beartype.typing import cast
from redisvl.query.query import VectorQuery, VectorRangeQuery

from superlinked.framework.common.const import Constants
from superlinked.framework.common.precision import Precision
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.storage.redis.query.redis_filter_builder import (
    RedisFilterBuilder,
)
from superlinked.framework.storage.redis.query.redis_vector_query_params import (
    HYBRID_POLICY_BATCHES,
    RedisVectorQueryParams,
    VectorQueryObj,
)
from superlinked.framework.storage.redis.query.vdb_knn_search_params import (
    RedisVDBKNNSearchConfig,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder


class RedisQueryBuilder:
    def __init__(self, encoder: RedisFieldEncoder, vector_precision: Precision) -> None:
        self._encoder = encoder
        self.filter_builder = RedisFilterBuilder(self._encoder)
        self._vector_precision = vector_precision
        self._timeout = Constants().REDIS_TIMEOUT

    def build_query(self, search_params: VDBKNNSearchParams, search_config: RedisVDBKNNSearchConfig) -> VectorQueryObj:
        params = self._build_params(search_params, search_config)
        return self._init_query_with_params(search_params, params)

    def _build_params(
        self, search_params: VDBKNNSearchParams, search_config: RedisVDBKNNSearchConfig
    ) -> RedisVectorQueryParams:
        vector = cast(bytes, self._encoder.encode_field(search_params.vector_field))
        return_fields = [returned_field.name for returned_field in search_params.fields_to_return]
        filter_expression = self.filter_builder.build(search_params.filters)
        hybrid_policy = self._override_hybrid_policy(search_params, search_config)
        return RedisVectorQueryParams(
            vector=vector,
            vector_field_name=search_params.vector_field.name,
            return_fields=return_fields,
            filter_expression=filter_expression,
            num_results=search_params.limit,
            hybrid_policy=hybrid_policy,
            batch_size=search_config.batch_size,
            dtype=self._vector_precision.value.lower(),
        )

    def _override_hybrid_policy(
        self, search_params: VDBKNNSearchParams, search_config: RedisVDBKNNSearchConfig
    ) -> str | None:
        if self._only_filtering_for_schema(search_params):
            return HYBRID_POLICY_BATCHES
        return search_config.hybrid_policy

    def _only_filtering_for_schema(self, search_params: VDBKNNSearchParams) -> bool:
        return not search_params.filters or len(search_params.filters) == 1

    def _init_query_with_params(
        self, search_params: VDBKNNSearchParams, params: RedisVectorQueryParams
    ) -> VectorQueryObj:
        if search_params.radius is not None:
            query = VectorRangeQuery(**asdict(params.with_radius(search_params.radius)))
        else:
            query = VectorQuery(**asdict(params))
        # timeout param is not available in RedisVL
        query._timeout = self._timeout  # redis returns no results if timeout reached
        return query
