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

from beartype.typing import Sequence, cast
from qdrant_client.models import Condition, Filter

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.storage.qdrant.qdrant_field_encoder import QdrantFieldEncoder
from superlinked.framework.storage.qdrant.query.qdrant_filter import (
    ClauseType,
    ContainsAllFilter,
    MatchAnyFilter,
    MatchRangeFilter,
    MatchValueFilter,
    QdrantFilter,
)
from superlinked.framework.storage.qdrant.query.qdrant_vdb_knn_search_params import (
    QdrantVDBKNNSearchParams,
)


@dataclass(frozen=True)
class QdrantQuery:
    collection_name: str
    vector: Vector
    filter_: Filter | None
    limit: int
    score_treshold: float | None
    with_vector: Sequence[str] | bool
    returned_payload_fields: Sequence[str]


FILTER_BY_OP_TYPE: dict[ComparisonOperationType, QdrantFilter] = {
    ComparisonOperationType.EQUAL: MatchValueFilter(ClauseType.MUST),
    ComparisonOperationType.NOT_EQUAL: MatchValueFilter(ClauseType.MUST_NOT),
    ComparisonOperationType.GREATER_THAN: MatchRangeFilter(ClauseType.MUST),
    ComparisonOperationType.LESS_THAN: MatchRangeFilter(ClauseType.MUST),
    ComparisonOperationType.GREATER_EQUAL: MatchRangeFilter(ClauseType.MUST),
    ComparisonOperationType.LESS_EQUAL: MatchRangeFilter(ClauseType.MUST),
    ComparisonOperationType.IN: MatchAnyFilter(ClauseType.MUST),
    ComparisonOperationType.NOT_IN: MatchAnyFilter(ClauseType.MUST_NOT),
    ComparisonOperationType.CONTAINS: MatchAnyFilter(ClauseType.MUST),
    ComparisonOperationType.NOT_CONTAINS: MatchAnyFilter(ClauseType.MUST_NOT),
    ComparisonOperationType.CONTAINS_ALL: ContainsAllFilter(ClauseType.MUST),
}


class QdrantQueryBuilder:
    def __init__(self, encoder: QdrantFieldEncoder) -> None:
        self._encoder = encoder

    def build(self, search_params: QdrantVDBKNNSearchParams) -> QdrantQuery:
        filter_ = self._compile_filters(search_params.filters)
        vector_field_name = search_params.vector_field.name
        returned_field_names = [field.name for field in search_params.fields_to_return]
        with_vector: list[str] | bool = [vector_field_name] if vector_field_name in returned_field_names else False
        returned_payload_fields = [field for field in returned_field_names if field != vector_field_name]
        return QdrantQuery(
            search_params.collection_name,
            search_params.vector_field.value,
            filter_,
            search_params.limit,
            1 - search_params.radius if search_params.radius is not None else None,
            with_vector,
            returned_payload_fields,
        )

    def _compile_filters(
        self,
        filters: Sequence[ComparisonOperation[Field]] | None,
    ) -> Filter | None:
        if not filters:
            return None

        grouped_filters = ComparisonOperation._group_filters_by_group_key(filters)
        compiled_filters = [
            self._compile_filter_for_group(group_key, group_filters)
            for group_key, group_filters in grouped_filters.items()
        ]
        return Filter(must=compiled_filters)

    def _compile_filter_for_group(self, group_key: int | None, filters: Sequence[ComparisonOperation]) -> Condition:
        conditions = [self._create_clause_condition(filter_) for filter_ in filters]
        return cast(
            Condition,
            Filter(
                must=conditions if group_key is None else [],
                should=conditions if group_key is not None else [],
            ),
        )

    def _create_clause_condition(self, filter_: ComparisonOperation[Field]) -> Condition:
        qdrant_filter = FILTER_BY_OP_TYPE[filter_._op]
        field_conditions = qdrant_filter.to_field_conditions(filter_, self._encoder)

        return cast(
            Condition,
            Filter(
                must=self._get_typed_conditions(field_conditions, qdrant_filter, ClauseType.MUST),
                must_not=self._get_typed_conditions(field_conditions, qdrant_filter, ClauseType.MUST_NOT),
            ),
        )

    def _get_typed_conditions(
        self, conditions: Sequence[Condition], filter_: QdrantFilter, target_type: ClauseType
    ) -> list[Condition]:
        return list(conditions) if filter_.clause_type == target_type else []
