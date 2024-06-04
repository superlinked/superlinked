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

from dataclasses import dataclass
from typing import Any, cast

from beartype.typing import Sequence
from redis.commands.search.query import Query

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData, VectorFieldData
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.storage.redis.query.redis_equality_filter import (
    RedisEqualityFilter,
)
from superlinked.framework.storage.redis.redis_field_encoder import RedisFieldEncoder

RANGE_DISTANCE_PARAM_NAME = "__range_dist"
VECTOR_SCORE_ALIAS = "__vector_score"


@dataclass
class RedisQuery:
    query: Query
    query_params: dict[str, Any]


class RedisQueryBuilder:
    def __init__(self, encoder: RedisFieldEncoder) -> None:
        self._encoder = encoder

    def build_query(
        self, search_params: VDBKNNSearchParams, returned_fields: Sequence[Field]
    ) -> RedisQuery:
        if search_params.limit is None:
            raise ValueError("Missing search limit")

        redis_filters = self._compile_filters_to_redis_filters(
            search_params.filters or []
        )

        vector_field_param_name = f"{search_params.vector_field.name}_param"
        query_string = self._create_query_string(
            redis_filters, search_params, vector_field_param_name
        )
        query = self._init_query(query_string, search_params.limit, returned_fields)
        query_params = self._get_query_params(
            redis_filters, search_params.vector_field, vector_field_param_name
        )
        return RedisQuery(query, query_params)

    def _compile_filters_to_redis_filters(
        self, filters: Sequence[ComparisonOperation[Field]]
    ) -> Sequence[RedisEqualityFilter]:
        return [
            RedisEqualityFilter(
                cast(Field, filter_._operand).name,
                self._encoder.encode_field(
                    FieldData.from_field(cast(Field, filter_._operand), filter_._other)
                ),
                filter_._op != ComparisonOperationType.EQUAL,
            )
            for filter_ in filters
        ]

    def _create_query_string(
        self,
        redis_filters: Sequence[RedisEqualityFilter],
        search_params: VDBKNNSearchParams,
        vector_field_param_name: str,
    ) -> str:
        prefilters = [redis_filter.get_prefix() for redis_filter in redis_filters]
        if search_params.radius is not None:
            radius_filter_str = self._create_radius_filter_str(
                search_params.vector_field,
                search_params.radius,
                vector_field_param_name,
            )
            prefilters.append(radius_filter_str)
        prefilter_str = f"({' '.join(prefilters)})" if prefilters else "*"
        return (
            f"{prefilter_str}=>[KNN {search_params.limit} "
            + f"@{search_params.vector_field.name} ${vector_field_param_name} AS {VECTOR_SCORE_ALIAS}]"
        )

    def _init_query(
        self, query_string: str, limit: int, returned_fields: Sequence[Field]
    ) -> Query:
        return (
            Query(query_string)
            .sort_by(VECTOR_SCORE_ALIAS, asc=True)
            .paging(0, limit)
            .return_fields(
                *(
                    [VECTOR_SCORE_ALIAS, f"{RANGE_DISTANCE_PARAM_NAME}"]
                    + [returned_field.name for returned_field in returned_fields]
                )
            )
            .dialect(2)
        )

    def _get_query_params(
        self,
        redis_filters: Sequence[RedisEqualityFilter],
        vector_field: VectorFieldData,
        vector_field_param_name: str,
    ) -> dict[str, Any]:
        query_params: dict[str, Any] = dict(
            {
                param
                for redis_filter in redis_filters
                for param in redis_filter.get_params()
            }
        )
        query_vector = self._encoder.encode_field(vector_field)
        query_params.update({vector_field_param_name: query_vector})
        return query_params

    def _create_radius_filter_str(
        self,
        vector_field: VectorFieldData,
        radius: float,
        vector_field_param_name: str,
    ) -> str:
        # Radius won't work perfectly on indices with IP distance metric!
        return (
            f"@{vector_field.name}:[VECTOR_RANGE {radius} ${vector_field_param_name}]"
            + f"=>{{$yield_distance_as: {RANGE_DISTANCE_PARAM_NAME}}}"
        )
