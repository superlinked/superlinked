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

from beartype.typing import Any, Sequence, cast
from typing_extensions import Self

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData
from superlinked.framework.common.storage.query.equality_filter import EqualityFilter
from superlinked.framework.storage.mongo.mongo_field_encoder import MongoFieldEncoder
from superlinked.framework.storage.mongo.query.mongo_vdb_knn_search_params import (
    MongoVDBKNNSearchParams,
)

# For more info on this check:
# https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
# paragraph Fields, 'numCandidates' definition.
VECTOR_SCORE_ALIAS = "__vector_score"


class MongoQuery:
    def __init__(self, encoder: MongoFieldEncoder) -> None:
        self._encoder = encoder
        self.__query = list[dict[str, dict[str, Any]]]()

    @property
    def query(self) -> Sequence[dict[str, dict[str, Any]]]:
        return self.__query

    # TODO FAI-1931: use pydantic for `query_parts`!
    def __add_query_part(self, query_part: dict[str, dict[str, Any]]) -> Self:
        if query_part:
            self.__query.append(query_part)
        return self

    def add_vector_search_dict(
        self,
        search_params: MongoVDBKNNSearchParams,
    ) -> Self:
        filters: dict[str, Any] = self._get_filters_dict(search_params.filters)
        return self.__add_query_part(
            {
                "$vectorSearch": {
                    "index": search_params.index_name,
                    "path": search_params.vector_field.name,
                    "queryVector": self._encoder.encode_field(
                        search_params.vector_field
                    ),
                    "numCandidates": search_params.num_candidates,
                    "limit": search_params.limit,
                    "filter": filters,
                }
            }
        )

    def add_radius_filter_dict(self, radius: float | None) -> Self:
        if radius is None:
            return self
        return self.__add_query_part(
            {"$match": {VECTOR_SCORE_ALIAS: {"$gt": 1 - radius}}}
        )

    def add_projection_dict(
        self,
        returned_fields: Sequence[Field],
    ) -> Self:
        field_set_dict: dict[str, Any] = {
            returned_field.name: 1 for returned_field in returned_fields
        }
        field_set_dict.update(
            {"_id": 1, VECTOR_SCORE_ALIAS: {"$meta": "vectorSearchScore"}}
        )
        return self.__add_query_part({"$project": field_set_dict})

    def _get_filters_dict(
        self, filters: Sequence[ComparisonOperation[Field]] | None
    ) -> dict[str, Any]:
        equality_filters = self._compile_filters(filters or [])
        if len(equality_filters) > 1:
            return {
                "$and": [
                    MongoQuery._equality_filters_to_dict(filter_)
                    for filter_ in equality_filters
                ]
            }
        if equality_filters:
            return MongoQuery._equality_filters_to_dict(equality_filters[0])
        return {}

    def _compile_filters(
        self, filters: Sequence[ComparisonOperation[Field]]
    ) -> Sequence[EqualityFilter]:
        return [
            EqualityFilter(
                cast(Field, filter_._operand).name,
                self._encoder.encode_field(
                    FieldData.from_field(cast(Field, filter_._operand), filter_._other)
                ),
                filter_._op != ComparisonOperationType.EQUAL,
            )
            for filter_ in filters
        ]

    @staticmethod
    def _equality_filters_to_dict(
        equality_filter: EqualityFilter,
    ) -> dict[str, dict[str, Any]]:
        return {
            equality_filter.field_name: {
                (
                    "$ne" if equality_filter.negated else "$eq"
                ): equality_filter.field_value
            }
        }
