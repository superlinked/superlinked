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


from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from beartype.typing import cast
from qdrant_client.models import FieldCondition, MatchAny, MatchValue, Range
from typing_extensions import override

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.storage.qdrant.qdrant_field_encoder import QdrantFieldEncoder


class ClauseType(Enum):
    MUST = "must"
    MUST_NOT = "must_not"


@dataclass(frozen=True)
class QdrantFilter(ABC):
    clause_type: ClauseType

    def extend_filters(
        self,
        filter_: ComparisonOperation[Field],
        encoder: QdrantFieldEncoder,
        must_filters: list[FieldCondition],
        must_not_filters: list[FieldCondition],
    ) -> None:
        filters_to_extend: list[FieldCondition]
        match self.clause_type:
            case ClauseType.MUST:
                filters_to_extend = must_filters
            case ClauseType.MUST_NOT:
                filters_to_extend = must_not_filters
        filters_to_extend.extend(self.to_field_conditions(filter_, encoder))

    @abstractmethod
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        pass

    def valid_types_string(self, valid_types: tuple[type, ...]) -> str:
        return ", ".join([t.__name__ for t in valid_types])


@dataclass(frozen=True)
class MatchValueFilter(QdrantFilter):
    valid_types = (bool, int, str)

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                match=self._encode_match_value_filter(filter_, encoder),
            )
        ]

    def _encode_match_value_filter(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> MatchValue:
        if not isinstance(filter_._other, MatchValueFilter.valid_types):
            raise ValueError(
                f"Qdrant only supports {self.valid_types_string(MatchValueFilter.valid_types)} "
                + f"{MatchValue.__name__}, got {type(filter_._other)}"
            )
        return MatchValue(
            value=encoder.encode_field(FieldData.from_field(cast(Field, filter_._operand), filter_._other))
        )


@dataclass(frozen=True)
class MatchAnyFilter(QdrantFilter):
    valid_types = (int, str)

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                match=self._encode_match_any_filter(filter_, encoder),
            )
        ]

    def _encode_match_any_filter(self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder) -> MatchAny:
        other = filter_._other if isinstance(filter_._other, list) else [filter_._other]
        if invalid_any := [type(o).__name__ for o in other if not isinstance(other, MatchAnyFilter.valid_types)]:
            raise ValueError(
                f"Qdrant only supports {self.valid_types_string(MatchAnyFilter.valid_types)} "
                + f"{MatchAny.__name__}, got {invalid_any}"
            )
        return MatchAny(
            any=[encoder.encode_field(FieldData.from_field(cast(Field, filter_._operand), o)) for o in other]
        )


@dataclass(frozen=True)
class MatchRangeFilter(QdrantFilter):
    valid_types = (float, int)
    range_arg_name_by_op_type = {
        ComparisonOperationType.GREATER_THAN: "gt",
        ComparisonOperationType.LESS_THAN: "lt",
        ComparisonOperationType.GREATER_EQUAL: "gte",
        ComparisonOperationType.LESS_EQUAL: "lte",
    }

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                range=self._encode_range_filter(filter_, encoder),
            )
        ]

    def _encode_range_filter(self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder) -> Range:
        if not isinstance(filter_._other, MatchRangeFilter.valid_types):
            raise ValueError(
                f"Qdrant only supports {self.valid_types_string(MatchRangeFilter.valid_types)} "
                + f"{MatchValue.__name__}, got {type(filter_._other)}"
            )
        range_args = {
            MatchRangeFilter.range_arg_name_by_op_type[filter_._op]: encoder.encode_field(
                FieldData.from_field(cast(Field, filter_._operand), filter_._other)
            )
        }
        return Range(**range_args)


@dataclass(frozen=True)
class ContainsAllFilter(MatchAnyFilter):
    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        other = filter_._other if isinstance(filter_._other, list) else [filter_._other]
        filter_per_other = [filter_._operand.contains_all(o) for o in other]
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                match=self._encode_match_any_filter(filter_, encoder),
            )
            for filter_ in filter_per_other
        ]
