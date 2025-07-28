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

from beartype.typing import Sequence

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.clause_params import KNNSearchClauseParams


@dataclass(frozen=True)
class KNNSearchParams:
    vector: Vector
    limit: int
    filters: Sequence[ComparisonOperation[SchemaField]]
    schema_fields_to_return: Sequence[SchemaField]
    radius: float | None
    should_return_index_vector: bool = False

    @classmethod
    def from_clause_params(cls, query_vector: Vector, partial: KNNSearchClauseParams) -> KNNSearchParams:
        if partial.limit is None:
            raise InvalidInputException(f"{cls.__name__} must have a valid limit, got None.")
        return cls(
            query_vector,
            partial.limit,
            partial.filters,
            partial.schema_fields_to_return,
            partial.radius,
            partial.should_return_index_vector,
        )
