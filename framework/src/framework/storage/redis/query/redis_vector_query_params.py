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

from beartype.typing import Sequence, TypeAlias
from redisvl.query.filter import FilterExpression
from redisvl.query.query import VectorQuery, VectorRangeQuery

from superlinked.framework.common.settings import Settings

VectorQueryObj: TypeAlias = VectorQuery | VectorRangeQuery
DISTANCE_ID: str = "vector_distance"


@dataclass(frozen=True)
class RedisVectorQueryParams:  # pylint: disable=too-many-instance-attributes
    vector: bytes
    vector_field_name: str
    return_fields: Sequence[str]
    filter_expression: FilterExpression
    num_results: int
    return_score: bool = True
    dialect: int = 2
    sort_by: str = DISTANCE_ID
    hybrid_policy: str | None = Settings().REDIS_HYBRID_POLICY
    batch_size: int | None = Settings().REDIS_BATCH_SIZE

    def with_radius(self, radius: float) -> "RedisVectorRangeQueryParams":
        return RedisVectorRangeQueryParams(
            vector=self.vector,
            vector_field_name=self.vector_field_name,
            return_fields=self.return_fields,
            filter_expression=self.filter_expression,
            num_results=self.num_results,
            return_score=self.return_score,
            dialect=self.dialect,
            sort_by=self.sort_by,
            distance_threshold=radius,
        )


@dataclass(frozen=True)
class RedisVectorRangeQueryParams(RedisVectorQueryParams):
    distance_threshold: float = 0.2
