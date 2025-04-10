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

from abc import ABC, abstractmethod
from collections import defaultdict

from beartype.typing import Any, Callable, Generic, Sequence, TypeVar, cast

from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.util.type_validator import TypeValidator

COT = TypeVar("COT", bound="ComparisonOperand")


class ComparisonOperand(ABC, Generic[COT]):
    def __init__(self, _: type[COT]) -> None:
        super().__init__()
        self.__built_in_operation_mapping: dict[str, Callable[[ComparisonOperand[COT], object], bool]] = {
            ComparisonOperationType.EQUAL.value: self._built_in_equal,
            ComparisonOperationType.NOT_EQUAL.value: self._built_in_not_equal,
            ComparisonOperationType.GREATER_THAN.value: self._built_in_greater_than,
            ComparisonOperationType.LESS_THAN.value: self._built_in_less_than,
            ComparisonOperationType.GREATER_EQUAL.value: self._built_in_greater_equal,
            ComparisonOperationType.LESS_EQUAL.value: self._built_in_less_equal,
            ComparisonOperationType.IN.value: self._built_in_in,
            ComparisonOperationType.NOT_IN.value: self._built_in_not_in,
            ComparisonOperationType.CONTAINS.value: self._built_in_contains,
            ComparisonOperationType.NOT_CONTAINS.value: self._built_in_not_contains,
            ComparisonOperationType.CONTAINS_ALL.value: self._built_in_contains_all,
        }

    def in_(self, __value: object) -> ComparisonOperation[COT]:
        return ComparisonOperation(ComparisonOperationType.IN, self, __value)

    def not_in_(self, __value: object) -> ComparisonOperation[COT]:
        return ComparisonOperation(ComparisonOperationType.NOT_IN, self, __value)

    def contains(self, __value: object) -> ComparisonOperation[COT]:
        return ComparisonOperation(ComparisonOperationType.CONTAINS, self, __value)

    def not_contains(self, __value: object) -> ComparisonOperation[COT]:
        return ComparisonOperation(ComparisonOperationType.NOT_CONTAINS, self, __value)

    def contains_all(self, __value: object) -> ComparisonOperation[COT]:
        return ComparisonOperation(ComparisonOperationType.CONTAINS_ALL, self, __value)

    def _get_built_in_operation(
        self, operation_type: ComparisonOperationType
    ) -> Callable[[ComparisonOperand[COT], object], bool]:
        return self.__built_in_operation_mapping[operation_type.value]

    def __eq__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.EQUAL, self, __value)

    @staticmethod
    @abstractmethod
    def _built_in_equal(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        pass

    def __ne__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.NOT_EQUAL, self, __value)

    @staticmethod
    @abstractmethod
    def _built_in_not_equal(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        pass

    def __gt__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.GREATER_THAN, self, __value)

    @staticmethod
    def _built_in_greater_than(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    def __lt__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.LESS_THAN, self, __value)

    @staticmethod
    def _built_in_less_than(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    def __ge__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.GREATER_EQUAL, self, __value)

    @staticmethod
    def _built_in_greater_equal(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    def __le__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.LESS_EQUAL, self, __value)

    @staticmethod
    def _built_in_less_equal(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _built_in_in(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _built_in_not_in(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _built_in_contains(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _built_in_not_contains(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _built_in_contains_all(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        raise NotImplementedError()


class _Or(Generic[COT]):
    def __init__(
        self,
        operations: Sequence[ComparisonOperation[COT]],
    ) -> None:
        self.operations = [
            ComparisonOperation(
                operation._op,
                operation._operand,
                operation._other,
                hash(self),
            )
            for operation in operations
        ]

    def __or__(self, other: COT) -> _Or:
        return _Or.combine_operations(self, other)

    def or_(self, other: COT) -> _Or:
        return self | other

    @staticmethod
    def _built_in_equal(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        if isinstance(left_operand, _Or) and isinstance(right_operand, _Or):
            return right_operand.operations == left_operand.operations
        return False

    @staticmethod
    def _built_in_not_equal(left_operand: ComparisonOperand[COT], right_operand: object) -> bool:
        return not _Or._built_in_equal(left_operand, right_operand)

    @staticmethod
    def combine_operations(first: COT | _Or, second: COT) -> _Or:
        return _Or(_Or._extract_operations(first) + _Or._extract_operations(second))

    @staticmethod
    def _extract_operations(operation: COT | _Or) -> list[ComparisonOperation[COT]]:
        if isinstance(operation, _Or):
            return operation.operations
        if isinstance(operation, ComparisonOperation):
            return [operation]
        raise ValueError(f"operand of or clause must be {ComparisonOperation} or {_Or}, got {type(operation)}.")


class ComparisonOperation(Generic[COT]):
    def __init__(
        self,
        op: ComparisonOperationType,
        operand: ComparisonOperand[COT],
        other: object,
        group_key: int | None = None,
    ) -> None:
        self._op = op
        self._operand = operand
        self._other = other
        self._group_key = group_key

    def __or__(self, other: Any) -> _Or:
        return _Or([self]) | other

    def or_(self, other: Any) -> _Or:
        return self | other

    def __bool__(self) -> bool:
        return self._operand._get_built_in_operation(self._op)(self._operand, self._other)

    def __str__(self) -> str:
        return f"{type(self).__name__}(op={self._op}, operand={self._operand}, other={self._other})"

    def evaluate(self, value: Any) -> bool:
        match self._op:
            case ComparisonOperationType.EQUAL:
                result = self.__evaluate_eq(value)
            case ComparisonOperationType.NOT_EQUAL:
                result = self.__evaluate_ne(value)
            case ComparisonOperationType.GREATER_THAN:
                result = self.__evaluate_gt(value)
            case ComparisonOperationType.LESS_THAN:
                result = self.__evaluate_lt(value)
            case ComparisonOperationType.GREATER_EQUAL:
                result = self.__evaluate_ge(value)
            case ComparisonOperationType.LESS_EQUAL:
                result = self.__evaluate_le(value)
            case ComparisonOperationType.IN:
                result = self.__evaluate_in(value)
            case ComparisonOperationType.NOT_IN:
                result = self.__evaluate_not_in(value)
            case ComparisonOperationType.CONTAINS:
                result = self.__evaluate_contains(value)
            case ComparisonOperationType.NOT_CONTAINS:
                result = self.__evaluate_not_contains(value)
            case ComparisonOperationType.CONTAINS_ALL:
                result = self.__evaluate_contains_all(value)
            case _:
                raise ValueError(f"Unsupported operation type: {self._op}")
        return result

    def __evaluate_eq(self, value: Any) -> bool:
        return value == self._other

    def __evaluate_ne(self, value: Any) -> bool:
        return value != self._other

    def __evaluate_gt(self, value: Any) -> bool:
        return value is not None and value > self._other

    def __evaluate_lt(self, value: Any) -> bool:
        return value is not None and value < self._other

    def __evaluate_ge(self, value: Any) -> bool:
        return value is not None and value >= self._other

    def __evaluate_le(self, value: Any) -> bool:
        return value is not None and value <= self._other

    def __evaluate_in(self, value: Any) -> bool:
        return value in self._get_other_as_sequence()

    def __evaluate_not_in(self, value: Any) -> bool:
        return value not in self._get_other_as_sequence()

    def __evaluate_contains(self, value: Any) -> bool:
        other = self._get_other_as_sequence()
        return value is not None and any(other in value for other in other)

    def __evaluate_not_contains(self, value: Any) -> bool:
        return value is not None and not self.__evaluate_contains(value)

    def __evaluate_contains_all(self, value: Any) -> bool:
        other = self._get_other_as_sequence()
        return value is None or all(other in value for other in other)

    def _get_other_as_sequence(self) -> Sequence[Any]:
        if TypeValidator.is_sequence_safe(self._other):
            return cast(Sequence, self._other)
        return [self._other]

    @staticmethod
    def _group_filters_by_group_key(
        filters: Sequence[ComparisonOperation[COT]],
    ) -> dict[int | None, list[ComparisonOperation[COT]]]:
        grouped_filters = defaultdict(list)
        for filter_ in filters:
            grouped_filters[filter_._group_key].append(filter_)
        return dict(grouped_filters)
