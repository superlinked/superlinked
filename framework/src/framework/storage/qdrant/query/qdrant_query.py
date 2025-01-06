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
from qdrant_client.models import Condition, FieldCondition, Filter

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
    with_vector: str | bool
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
        with_vector: str | bool = vector_field_name if vector_field_name in returned_field_names else False
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
        # Mutable lists!
        must_filters = list[FieldCondition]()
        must_not_filters = list[FieldCondition]()
        for filter_ in filters:
            qdrant_filter = FILTER_BY_OP_TYPE[filter_._op]
            # Extends lists!
            qdrant_filter.extend_filters(filter_, self._encoder, must_filters, must_not_filters)
        # casting is needed as Filter only accepts `Condition` type but it also works with FieldCondition
        return Filter(must=cast(list[Condition], must_filters), must_not=cast(list[Condition], must_not_filters))
