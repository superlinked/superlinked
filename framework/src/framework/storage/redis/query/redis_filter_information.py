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

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce

from beartype.typing import Any, Sequence
from redisvl.query.filter import FilterExpression, FilterOperator

from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)


class FilterCombinator:
    @staticmethod
    def combine_with_and(expressions: Sequence[FilterExpression]) -> FilterExpression:
        return reduce(lambda x, y: x & y, expressions)

    @staticmethod
    def combine_with_or(expressions: Sequence[FilterExpression]) -> FilterExpression:
        return reduce(lambda x, y: x | y, expressions)

    @staticmethod
    def get_single_expression(expressions: Sequence[FilterExpression]) -> FilterExpression:
        if len(expressions) != 1:
            raise ValueError(f"Expected exactly one expression, but got {len(expressions)}")
        return expressions[0]


class FilterValueMapper:
    @staticmethod
    def value_as_is(field_value: Any) -> list[Any]:
        return field_value

    @staticmethod
    def comma_separated_single_list_in_a_list(field_value: Any) -> list[Any]:
        return [[field] for field in FilterValueMapper._split_comma_separated_bytes(field_value)]

    @staticmethod
    def value_in_a_list(field_value: Any) -> list[Any]:
        return [field_value]

    @staticmethod
    def comma_separated_list_in_a_list(field_value: Any) -> list[Any]:
        return [FilterValueMapper._split_comma_separated_bytes(field_value)]

    @staticmethod
    def _split_comma_separated_bytes(value: bytes) -> list[str]:
        return value.decode("utf-8").split(", ")


class CombinationFnKey(Enum):
    SINGLE_EXPRESSION = auto()
    COMBINE_WITH_AND = auto()
    COMBINE_WITH_OR = auto()


class ValueMapperFnKey(Enum):
    VALUE_AS_IS = auto()
    COMMA_SEPARATED_SINGLE_LIST_IN_A_LIST = auto()
    VALUE_IN_A_LIST = auto()
    COMMA_SEPARATED_LIST_IN_A_LIST = auto()


COMBINATION_FN_MAP: dict[CombinationFnKey, Callable[[Sequence[FilterExpression]], FilterExpression]] = {
    CombinationFnKey.SINGLE_EXPRESSION: FilterCombinator.get_single_expression,
    CombinationFnKey.COMBINE_WITH_AND: FilterCombinator.combine_with_and,
    CombinationFnKey.COMBINE_WITH_OR: FilterCombinator.combine_with_or,
}

VALUE_MAPPER_FN_MAP: dict[ValueMapperFnKey, Callable[[Any], Sequence[Any]]] = {
    ValueMapperFnKey.VALUE_AS_IS: FilterValueMapper.value_as_is,
    ValueMapperFnKey.COMMA_SEPARATED_SINGLE_LIST_IN_A_LIST: FilterValueMapper.comma_separated_single_list_in_a_list,
    ValueMapperFnKey.VALUE_IN_A_LIST: FilterValueMapper.value_in_a_list,
    ValueMapperFnKey.COMMA_SEPARATED_LIST_IN_A_LIST: FilterValueMapper.comma_separated_list_in_a_list,
}


@dataclass(frozen=True)
class RedisFilterInformation:
    filter_operator: FilterOperator
    combination_fn_key: CombinationFnKey
    value_mapper_fn_key: ValueMapperFnKey

    def get_combination_fn(self) -> Callable[[Sequence[FilterExpression]], FilterExpression]:
        return COMBINATION_FN_MAP[self.combination_fn_key]

    def get_value_mapper_fn(self) -> Callable[[Any], Sequence[Any]]:
        return VALUE_MAPPER_FN_MAP[self.value_mapper_fn_key]

    @staticmethod
    def get(operation_type: ComparisonOperationType) -> "RedisFilterInformation":
        if operation_type not in FILTER_INFORMATION_BY_COMPARISON_OPERATION_TYPE:
            raise KeyError(f"Unsupported operation type: {operation_type}")
        return FILTER_INFORMATION_BY_COMPARISON_OPERATION_TYPE[operation_type]


FILTER_INFORMATION_BY_COMPARISON_OPERATION_TYPE: dict[ComparisonOperationType, RedisFilterInformation] = {
    ComparisonOperationType.EQUAL: RedisFilterInformation(
        FilterOperator.EQ, CombinationFnKey.SINGLE_EXPRESSION, ValueMapperFnKey.VALUE_IN_A_LIST
    ),
    ComparisonOperationType.NOT_EQUAL: RedisFilterInformation(
        FilterOperator.NE, CombinationFnKey.SINGLE_EXPRESSION, ValueMapperFnKey.VALUE_IN_A_LIST
    ),
    ComparisonOperationType.GREATER_THAN: RedisFilterInformation(
        FilterOperator.GT, CombinationFnKey.SINGLE_EXPRESSION, ValueMapperFnKey.VALUE_IN_A_LIST
    ),
    ComparisonOperationType.LESS_THAN: RedisFilterInformation(
        FilterOperator.LT, CombinationFnKey.SINGLE_EXPRESSION, ValueMapperFnKey.VALUE_IN_A_LIST
    ),
    ComparisonOperationType.GREATER_EQUAL: RedisFilterInformation(
        FilterOperator.GE, CombinationFnKey.SINGLE_EXPRESSION, ValueMapperFnKey.VALUE_IN_A_LIST
    ),
    ComparisonOperationType.LESS_EQUAL: RedisFilterInformation(
        FilterOperator.LE, CombinationFnKey.SINGLE_EXPRESSION, ValueMapperFnKey.VALUE_IN_A_LIST
    ),
    ComparisonOperationType.IN: RedisFilterInformation(
        FilterOperator.EQ, CombinationFnKey.COMBINE_WITH_OR, ValueMapperFnKey.VALUE_AS_IS
    ),
    ComparisonOperationType.NOT_IN: RedisFilterInformation(
        FilterOperator.NE, CombinationFnKey.COMBINE_WITH_AND, ValueMapperFnKey.VALUE_AS_IS
    ),
    ComparisonOperationType.CONTAINS: RedisFilterInformation(
        FilterOperator.EQ, CombinationFnKey.COMBINE_WITH_OR, ValueMapperFnKey.COMMA_SEPARATED_LIST_IN_A_LIST
    ),
    ComparisonOperationType.NOT_CONTAINS: RedisFilterInformation(
        FilterOperator.NE, CombinationFnKey.COMBINE_WITH_AND, ValueMapperFnKey.COMMA_SEPARATED_LIST_IN_A_LIST
    ),
    ComparisonOperationType.CONTAINS_ALL: RedisFilterInformation(
        FilterOperator.EQ, CombinationFnKey.COMBINE_WITH_AND, ValueMapperFnKey.COMMA_SEPARATED_SINGLE_LIST_IN_A_LIST
    ),
}
