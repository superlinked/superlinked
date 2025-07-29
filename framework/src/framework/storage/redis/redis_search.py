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
from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import (
    RequestTimeoutException,
    UnexpectedResponseException,
)
from superlinked.framework.common.precision import Precision
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.search import Search
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.storage.redis.query.redis_query_builder import (
    RedisQueryBuilder,
    VectorQueryObj,
)
from superlinked.framework.storage.redis.query.redis_vector_query_params import (
    DISTANCE_ID,
)
from superlinked.framework.storage.redis.query.vdb_knn_search_params import (
    RedisVDBKNNSearchConfig,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder
from superlinked.framework.storage.redis.redis_knn_result import RedisKNNResult
from superlinked.framework.storage.redis.redis_vdb_client import RedisVDBClient

logger = structlog.getLogger()

EXTRA_ATTRIBUTES_BYTES_KEY = b"extra_attributes"
RESULTS_BYTES_KEY = b"results"
ID_BYTES_KEY = b"id"
UTF_8 = "utf-8"


class RedisSearch(Search[VDBKNNSearchParams, VectorQueryObj, list[RedisKNNResult], RedisVDBKNNSearchConfig]):
    def __init__(self, client: RedisVDBClient, encoder: RedisFieldEncoder, vector_precision: Precision) -> None:
        super().__init__()
        self._client = client
        self._encoder = encoder
        self._query_builder = RedisQueryBuilder(encoder, vector_precision)

    @override
    def build_query(self, search_params: VDBKNNSearchParams, search_config: RedisVDBKNNSearchConfig) -> VectorQueryObj:
        return self._query_builder.build_query(search_params, search_config)

    @override
    async def knn_search(
        self,
        index_config: IndexConfig,
        query: VectorQueryObj,
    ) -> list[RedisKNNResult]:
        result = await self._client.client.ft(index_config.index_name).search(query.query, query.params)
        return self._parse_knn_results(result, query._return_fields)

    def _parse_knn_results(
        self, knn_response: dict[bytes, Any] | Any, field_names: Sequence[str]
    ) -> list[RedisKNNResult]:
        self._validate_knn_response_format(knn_response)
        return [
            result
            for knn_result in knn_response[RESULTS_BYTES_KEY]
            if (result := self._parse_knn_result(knn_result, field_names)) is not None
        ]

    def _validate_knn_response_format(self, knn_response: dict[bytes, Any]) -> None:
        if not isinstance(knn_response, dict):
            raise RequestTimeoutException(f"Redis timeout ({constants.REDIS_TIMEOUT}ms) exceeded.")
        if RESULTS_BYTES_KEY not in knn_response:
            raise UnexpectedResponseException("Redis response missing results key.")

    def _parse_knn_result(
        self, knn_result: dict[bytes, Any] | None, field_names: Sequence[str]
    ) -> RedisKNNResult | None:
        if knn_result is None:
            raise UnexpectedResponseException("Redis returned incomplete results.")
        entity_id = self._get_entity_id_from_redis_id(knn_result.get(ID_BYTES_KEY))
        unnormalized_extra_attributes = knn_result.get(EXTRA_ATTRIBUTES_BYTES_KEY)
        if unnormalized_extra_attributes is None:
            logger.warning(
                "Redis result entry is missing extra attributes. "
                "Final results list will be shorter than required by `limit` parameter. "
                "Probable reason: concurrent writes to the VDB."
            )
            return None
        extra_attributes = self._normalize_extra_attributes(unnormalized_extra_attributes)
        score = self._extract_score(extra_attributes.get(DISTANCE_ID))
        field_name_to_data = self._extract_field_data(extra_attributes, field_names)
        return RedisKNNResult(entity_id=entity_id, score=score, field_name_to_data=field_name_to_data)

    def _normalize_extra_attributes(self, extra_attributes: dict[bytes, bytes] | Sequence[bytes]) -> dict[str, bytes]:
        if not extra_attributes:
            raise UnexpectedResponseException("Redis result missing extra attributes.")
        if isinstance(extra_attributes, dict):
            return self._convert_extra_attributes_keys_to_str(extra_attributes)
        if TypeValidator.is_sequence_safe(extra_attributes):
            return self._convert_sequence_to_dict(extra_attributes)
        raise UnexpectedResponseException(
            f"Redis returned unsupported extra attributes format: {type(extra_attributes)}."
        )

    def _convert_extra_attributes_keys_to_str(self, attributes: dict[bytes, bytes]) -> dict[str, bytes]:
        if not all(isinstance(key, bytes) for key in attributes.keys()):
            raise UnexpectedResponseException("Redis returned malformed extra attributes keys.")
        if not all(isinstance(value, bytes) for value in attributes.values()):
            raise UnexpectedResponseException("Redis returned malformed extra attributes values.")
        return {key.decode(UTF_8): attribute for key, attribute in attributes.items()}

    def _convert_sequence_to_dict(self, attributes: Sequence[bytes]) -> dict[str, bytes]:
        if len(attributes) % 2 != 0:
            raise UnexpectedResponseException("Redis returned malformed extra attributes sequence.")
        if not all(isinstance(item, bytes) for item in attributes):
            raise UnexpectedResponseException("Redis returned invalid attribute format.")
        return {attributes[i].decode(UTF_8): attributes[i + 1] for i in range(0, len(attributes), 2)}

    def _extract_field_data(self, attributes: dict[str, bytes], field_names: Sequence[str]) -> dict[str, Any]:
        return {field_name: attributes.get(field_name) for field_name in field_names}

    def _extract_score(self, distance: bytes | None) -> float:
        if distance is None:
            raise UnexpectedResponseException("Redis result is missing distance key.")
        return self._convert_distance_to_score(self._encoder._decode_double(distance))

    def _convert_distance_to_score(self, distance: float) -> float:
        return 1 - distance

    def _get_entity_id_from_redis_id(self, redis_id: bytes | None) -> EntityId:
        if redis_id is None:
            raise UnexpectedResponseException("Redis result is missing ID key.")
        return self._encoder.decode_redis_id_to_entity_id(redis_id)
