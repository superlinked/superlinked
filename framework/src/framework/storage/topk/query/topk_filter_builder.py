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


from beartype.typing import Any, Sequence, cast

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperand,
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ITERABLE_COMPARISON_OPERATION_TYPES,
    LIST_TYPE_COMPATIBLE_TYPES,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.storage.topk.query.topk_filter import TopKFilter
from superlinked.framework.storage.topk.query.topk_filter_information import (
    FilterCombinator,
)
from superlinked.framework.storage.topk.topk_field_encoder import (
    TopKEncodedTypes,
    TopKFieldEncoder,
)


class TopKFilterBuilder:
    def __init__(self, encoder: TopKFieldEncoder) -> None:
        self._encoder = encoder

    def build(self, filters: Sequence[ComparisonOperation[Field]]) -> Any:
        grouped_filters = ComparisonOperation._group_filters_by_group_key(filters)
        expressions_by_group = {
            group_key: self._compile_filters_to_expressions(filters) for group_key, filters in grouped_filters.items()
        }
        combined_expressions = [
            (
                FilterCombinator.combine_with_or(expressions)
                if group_key is not None
                else FilterCombinator.combine_with_and(expressions)
            )
            for group_key, expressions in expressions_by_group.items()
        ]

        if len(combined_expressions) == 1:
            return FilterCombinator.get_single_expression(combined_expressions)

        return FilterCombinator.combine_with_and(combined_expressions)

    def _compile_filters_to_expressions(self, filters: Sequence[ComparisonOperation[Field]]) -> list[Any]:
        return [self._compile_filter(filter_).to_expression() for filter_ in filters]

    def _compile_filter(self, filter_: ComparisonOperation[Field]) -> TopKFilter:
        other = (
            self._get_other_as_sequence(filter_._other) if filter_._op in LIST_TYPE_COMPATIBLE_TYPES else filter_._other
        )
        field_value = (
            self._encode_iterable_field(filter_._operand, other)
            if filter_._op in ITERABLE_COMPARISON_OPERATION_TYPES
            else self._encode_field(filter_._operand, other)
        )
        return TopKFilter(cast(Field, filter_._operand), field_value, filter_._op)

    def _get_other_as_sequence(self, other: Any) -> Sequence[Any]:
        if TypeValidator.is_sequence_safe(other):
            return cast(Sequence, other)
        return [other]

    def _encode_iterable_field(self, operand: ComparisonOperand, other: Any) -> list[TopKEncodedTypes]:
        return [self._encode_field(operand, item) for item in other]

    def _encode_field(self, operand: ComparisonOperand, other: object) -> TopKEncodedTypes:
        return self._encoder.encode_field(FieldData.from_field(cast(Field, operand), other))
