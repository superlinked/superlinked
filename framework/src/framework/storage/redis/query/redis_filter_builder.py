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
from redisvl.query.filter import FilterExpression

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
from superlinked.framework.storage.redis.query.redis_filter import RedisFilter
from superlinked.framework.storage.redis.query.redis_filter_information import (
    FilterCombinator,
)
from superlinked.framework.storage.redis.redis_field_encoder import (
    RedisEncodedTypes,
    RedisFieldEncoder,
)


class RedisFilterBuilder:
    def __init__(self, encoder: RedisFieldEncoder) -> None:
        self._encoder = encoder

    def build(self, filters: Sequence[ComparisonOperation[Field]] | None) -> FilterExpression:
        if not filters:
            return FilterExpression("*")

        grouped_filters = ComparisonOperation._group_filters_by_group_key(filters)
        expressions_by_group = {
            group_key: self._compile_filters_to_expressions(filters) for group_key, filters in grouped_filters.items()
        }
        combined_expressions = [
            self._combine_expressions(group_key, expressions) for group_key, expressions in expressions_by_group.items()
        ]
        if len(combined_expressions) == 1:
            return combined_expressions[0]
        return FilterCombinator.combine_with_and(combined_expressions)

    def _compile_filters_to_expressions(
        self, filters: Sequence[ComparisonOperation[Field]]
    ) -> Sequence[FilterExpression]:
        return [self._compile_filter(filter_).to_expression() for filter_ in filters]

    def _combine_expressions(self, group_key: int | None, expressions: Sequence[FilterExpression]) -> FilterExpression:
        if group_key is None:
            return FilterCombinator.combine_with_and(expressions)
        return FilterCombinator.combine_with_or(expressions)

    def _compile_filter(self, filter_: ComparisonOperation[Field]) -> RedisFilter:
        other = (
            self._get_other_as_sequence(filter_._other) if filter_._op in LIST_TYPE_COMPATIBLE_TYPES else filter_._other
        )
        field_value = (
            self._encode_iterable_field(filter_._operand, other)
            if filter_._op in ITERABLE_COMPARISON_OPERATION_TYPES
            else self._encode_field(filter_._operand, other)
        )
        return RedisFilter(cast(Field, filter_._operand), field_value, filter_._op)

    def _get_other_as_sequence(self, other: Any) -> Sequence[Any]:
        if TypeValidator.is_sequence_safe(other):
            return cast(Sequence, other)
        return [other]

    def _encode_iterable_field(self, operand: ComparisonOperand, other: Any) -> list[RedisEncodedTypes]:
        return [self._encode_field(operand, item) for item in other]

    def _encode_field(self, operand: ComparisonOperand, other: object) -> RedisEncodedTypes:
        return self._encoder.encode_field(FieldData.from_field(cast(Field, operand), other))
