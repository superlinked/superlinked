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
from typing import Any, Callable, Generic, TypeVar

from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)

COT = TypeVar("COT", bound="ComparisonOperand")


class ComparisonOperand(ABC, Generic[COT]):
    def __init__(self, _: type[COT]) -> None:
        super().__init__()
        self.__original_operation_mapping: dict[
            ComparisonOperationType, Callable[[ComparisonOperand[COT], object], bool]
        ] = {
            ComparisonOperationType.EQUAL: self._original_equal,
            ComparisonOperationType.NOT_EQUAL: self._original_not_equal,
            ComparisonOperationType.GREATER_THAN: self._original_greater_than,
            ComparisonOperationType.LESS_THAN: self._original_less_than,
            ComparisonOperationType.GREATER_EQUAL: self._original_greater_equal,
            ComparisonOperationType.LESS_EQUAL: self._original_less_equal,
        }

    @property
    def _original_operation_mapping(
        self,
    ) -> dict[
        ComparisonOperationType, Callable[[ComparisonOperand[COT], object], bool]
    ]:
        return self.__original_operation_mapping

    def _get_original_operation(
        self, operation_type: ComparisonOperationType
    ) -> Callable[[ComparisonOperand[COT], object], bool]:
        return self.__original_operation_mapping[operation_type]

    def __eq__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.EQUAL, self, __value)

    @staticmethod
    @abstractmethod
    def _original_equal(
        left_operand: ComparisonOperand[COT], right_operand: object
    ) -> bool:
        pass

    def __ne__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.NOT_EQUAL, self, __value)

    @staticmethod
    @abstractmethod
    def _original_not_equal(
        left_operand: ComparisonOperand[COT], right_operand: object
    ) -> bool:
        pass

    def __gt__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.GREATER_THAN, self, __value)

    @staticmethod
    def _original_greater_than(
        left_operand: ComparisonOperand[COT], right_operand: object
    ) -> bool:
        raise NotImplementedError()

    def __lt__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.LESS_THAN, self, __value)

    @staticmethod
    def _original_less_than(
        left_operand: ComparisonOperand[COT], right_operand: object
    ) -> bool:
        raise NotImplementedError()

    def __ge__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.GREATER_EQUAL, self, __value)

    @staticmethod
    def _original_greater_equal(
        left_operand: ComparisonOperand[COT], right_operand: object
    ) -> bool:
        raise NotImplementedError()

    def __le__(self, __value: object) -> ComparisonOperation[COT]:  # type: ignore[override]
        return ComparisonOperation(ComparisonOperationType.LESS_EQUAL, self, __value)

    @staticmethod
    def _original_less_equal(
        left_operand: ComparisonOperand[COT], right_operand: object
    ) -> bool:
        raise NotImplementedError()


class ComparisonOperation(Generic[COT]):
    def __init__(
        self,
        op: ComparisonOperationType,
        operand: ComparisonOperand[COT],
        other: object,
    ) -> None:
        self._op = op
        self._operand = operand
        self._other = other

    def __bool__(self) -> bool:
        return self._operand._get_original_operation(self._op)(
            self._operand, self._other
        )

    def evaluate(self, value: Any) -> bool:
        match self._op:
            case ComparisonOperationType.EQUAL:
                return self.__evaluate_eq(value)

            case ComparisonOperationType.NOT_EQUAL:
                return self.__evaluate_ne(value)

            case ComparisonOperationType.GREATER_THAN:
                return self.__evaluate_gt(value)

            case ComparisonOperationType.LESS_THAN:
                return self.__evaluate_lt(value)

            case ComparisonOperationType.GREATER_EQUAL:
                return self.__evaluate_ge(value)

            case ComparisonOperationType.LESS_EQUAL:
                return self.__evaluate_le(value)

    def __evaluate_eq(self, value: Any) -> bool:
        return value == self._other

    def __evaluate_ne(self, value: Any) -> bool:
        return value != self._other

    def __evaluate_gt(self, value: Any) -> bool:
        return value > self._other

    def __evaluate_lt(self, value: Any) -> bool:
        return value < self._other

    def __evaluate_ge(self, value: Any) -> bool:
        return value >= self._other

    def __evaluate_le(self, value: Any) -> bool:
        return value <= self._other
