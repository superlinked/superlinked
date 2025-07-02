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

from __future__ import annotations

from dataclasses import dataclass

from beartype.typing import Sequence, TypeAlias
from redisvl.query.filter import FilterExpression
from redisvl.query.query import VectorQuery, VectorRangeQuery

VectorQueryObj: TypeAlias = VectorQuery | VectorRangeQuery
DISTANCE_ID: str = "vector_distance"

HYBRID_POLICY_BATCHES = "BATCHES"
HYBRID_POLICY_ADHOC_BF = "ADHOC_BF"


@dataclass(frozen=True)
class RedisVectorQueryParams:  # pylint: disable=too-many-instance-attributes
    vector: bytes
    vector_field_name: str
    return_fields: Sequence[str]
    filter_expression: FilterExpression
    dtype: str
    num_results: int
    return_score: bool = True
    dialect: int = 2
    sort_by: str = DISTANCE_ID
    hybrid_policy: str | None = None
    batch_size: int | None = None

    def with_radius(self, radius: float) -> RedisVectorRangeQueryParams:
        return RedisVectorRangeQueryParams(
            vector=self.vector,
            vector_field_name=self.vector_field_name,
            return_fields=self.return_fields,
            filter_expression=self.filter_expression,
            dtype=self.dtype,
            num_results=self.num_results,
            return_score=self.return_score,
            dialect=self.dialect,
            sort_by=self.sort_by,
            hybrid_policy=self.hybrid_policy,
            batch_size=self.batch_size,
            distance_threshold=radius,
        )


@dataclass(frozen=True)
class RedisVectorRangeQueryParams(RedisVectorQueryParams):
    distance_threshold: float = 0.2
