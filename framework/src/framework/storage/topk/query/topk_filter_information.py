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

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce

from beartype.typing import Any, Sequence

from superlinked.framework.common.exception import (
    InvalidStateException,
    NotImplementedException,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)


class FilterOperator(Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GE = "ge"
    LE = "le"
    IN = "in"
    NOT_IN = "not_in"


class FilterCombinator:
    @staticmethod
    def combine_with_and(expressions: Sequence[Any]) -> Any:
        return reduce(lambda x, y: x & y, expressions)

    @staticmethod
    def combine_with_or(expressions: Sequence[Any]) -> Any:
        return reduce(lambda x, y: x | y, expressions)

    @staticmethod
    def get_single_expression(
        expressions: Sequence[Any],
    ) -> Any:
        if len(expressions) != 1:
            raise InvalidStateException("Expected exactly one expression.", expressions_length=len(expressions))
        return expressions[0]


class FilterValueMapper:
    @staticmethod
    def value_as_is(field_value: Any) -> Any:
        return field_value

    @staticmethod
    def comma_separated_single_list_in_a_list(field_value: str) -> list[list[Any]]:
        return [[field] for field in field_value.split(", ")]

    @staticmethod
    def value_in_a_list(field_value: Any) -> list[Any]:
        return [field_value]

    @staticmethod
    def comma_separated_list_in_a_list(field_value: str) -> list[list[Any]]:
        return [field_value.split(", ")]


class CombinationFnKey(Enum):
    SINGLE_EXPRESSION = auto()
    COMBINE_WITH_AND = auto()
    COMBINE_WITH_OR = auto()


class ValueMapperFnKey(Enum):
    VALUE_AS_IS = auto()
    COMMA_SEPARATED_SINGLE_LIST_IN_A_LIST = auto()
    VALUE_IN_A_LIST = auto()
    COMMA_SEPARATED_LIST_IN_A_LIST = auto()


COMBINATION_FN_MAP: dict[CombinationFnKey, Callable[[Sequence[Any]], Any]] = {
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
class TopKFilterInformation:
    filter_operator: FilterOperator
    combination_fn_key: CombinationFnKey
    value_mapper_fn_key: ValueMapperFnKey

    def get_combination_fn(
        self,
    ) -> Callable[[Sequence[Any]], Any]:
        return COMBINATION_FN_MAP[self.combination_fn_key]

    def get_value_mapper_fn(self) -> Callable[[Any], Sequence[Any]]:
        return VALUE_MAPPER_FN_MAP[self.value_mapper_fn_key]

    @staticmethod
    def get(operation_type: ComparisonOperationType) -> TopKFilterInformation:
        if operation_type not in FILTER_INFORMATION_BY_COMPARISON_OPERATION_TYPE:
            raise NotImplementedException("Unsupported operation type.", operation_type=operation_type)
        return FILTER_INFORMATION_BY_COMPARISON_OPERATION_TYPE[operation_type]


FILTER_INFORMATION_BY_COMPARISON_OPERATION_TYPE: dict[ComparisonOperationType, TopKFilterInformation] = {
    ComparisonOperationType.EQUAL: TopKFilterInformation(
        FilterOperator.EQ,
        CombinationFnKey.SINGLE_EXPRESSION,
        ValueMapperFnKey.VALUE_IN_A_LIST,
    ),
    ComparisonOperationType.NOT_EQUAL: TopKFilterInformation(
        FilterOperator.NE,
        CombinationFnKey.SINGLE_EXPRESSION,
        ValueMapperFnKey.VALUE_IN_A_LIST,
    ),
    ComparisonOperationType.GREATER_THAN: TopKFilterInformation(
        FilterOperator.GT,
        CombinationFnKey.SINGLE_EXPRESSION,
        ValueMapperFnKey.VALUE_IN_A_LIST,
    ),
    ComparisonOperationType.LESS_THAN: TopKFilterInformation(
        FilterOperator.LT,
        CombinationFnKey.SINGLE_EXPRESSION,
        ValueMapperFnKey.VALUE_IN_A_LIST,
    ),
    ComparisonOperationType.GREATER_EQUAL: TopKFilterInformation(
        FilterOperator.GE,
        CombinationFnKey.SINGLE_EXPRESSION,
        ValueMapperFnKey.VALUE_IN_A_LIST,
    ),
    ComparisonOperationType.LESS_EQUAL: TopKFilterInformation(
        FilterOperator.LE,
        CombinationFnKey.SINGLE_EXPRESSION,
        ValueMapperFnKey.VALUE_IN_A_LIST,
    ),
    ComparisonOperationType.IN: TopKFilterInformation(
        FilterOperator.EQ,
        CombinationFnKey.COMBINE_WITH_OR,
        ValueMapperFnKey.VALUE_AS_IS,
    ),
    ComparisonOperationType.NOT_IN: TopKFilterInformation(
        FilterOperator.NE,
        CombinationFnKey.COMBINE_WITH_AND,
        ValueMapperFnKey.VALUE_AS_IS,
    ),
    ComparisonOperationType.CONTAINS: TopKFilterInformation(
        FilterOperator.EQ,
        CombinationFnKey.COMBINE_WITH_OR,
        ValueMapperFnKey.COMMA_SEPARATED_LIST_IN_A_LIST,
    ),
    ComparisonOperationType.NOT_CONTAINS: TopKFilterInformation(
        FilterOperator.NE,
        CombinationFnKey.COMBINE_WITH_AND,
        ValueMapperFnKey.COMMA_SEPARATED_LIST_IN_A_LIST,
    ),
    ComparisonOperationType.CONTAINS_ALL: TopKFilterInformation(
        FilterOperator.EQ,
        CombinationFnKey.COMBINE_WITH_AND,
        ValueMapperFnKey.COMMA_SEPARATED_SINGLE_LIST_IN_A_LIST,
    ),
}
