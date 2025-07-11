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
from dataclasses import dataclass

from beartype.typing import Callable, Generic, TypeVar
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext

StepInputT = TypeVar("StepInputT")
StepInbetweenT = TypeVar("StepInbetweenT")
StepOutputT = TypeVar("StepOutputT")
StepCombinedOutputT = TypeVar("StepCombinedOutputT")


class Step(ABC, Generic[StepInputT, StepOutputT]):
    @abstractmethod
    async def transform(
        self,
        input_: StepInputT,
        context: ExecutionContext,
    ) -> StepOutputT:
        pass

    def combine(self, step: Step[StepOutputT, StepCombinedOutputT]) -> Transform[StepInputT, StepCombinedOutputT]:
        return Transform(self, step)

    def combine_if(
        self, step: Step[StepOutputT, StepCombinedOutputT], predicate: FilterPredicate[StepInputT, StepCombinedOutputT]
    ) -> Transform[StepInputT, StepCombinedOutputT]:
        return Transform(self, step, predicate)

    def __mul__(self, step: Step[StepOutputT, StepCombinedOutputT]) -> Transform[StepInputT, StepCombinedOutputT]:
        return self.combine(step)


@dataclass(frozen=True)
class FilterPredicate(Generic[StepInputT, StepCombinedOutputT]):
    filter_: Callable[[StepInputT], StepInputT | None]
    default_value: StepCombinedOutputT


class Transform(Generic[StepInputT, StepOutputT], Step[StepInputT, StepOutputT]):
    def __init__(
        self,
        step1: Step[StepInputT, StepInbetweenT],
        step2: Step[StepInbetweenT, StepOutputT],
        predicate: FilterPredicate | None = None,
    ) -> None:
        super().__init__()
        self._step1 = step1
        self._step2 = step2
        self._predicate = predicate

    @override
    async def transform(
        self,
        input_: StepInputT,
        context: ExecutionContext,
    ) -> StepOutputT:
        if self._predicate:
            result = self._predicate.filter_(input_)
            if result is None:
                return self._predicate.default_value
            input_ = result
        return await self._step2.transform(await self._step1.transform(input_, context), context)


WrapperInputT = TypeVar("WrapperInputT")
WrapperOutputT = TypeVar("WrapperOutputT")
WrappingContextT = TypeVar("WrappingContextT")


@dataclass(frozen=True)
class WrappingResult(Generic[StepInputT, WrappingContextT]):
    value: StepInputT
    context: WrappingContextT


class WrapperStep(
    Generic[WrapperInputT, WrapperOutputT, WrappingContextT, StepInputT, StepOutputT],
    Step[WrapperInputT, WrapperOutputT],
    ABC,
):
    def __init__(self, step: Step[StepInputT, StepOutputT]) -> None:
        super().__init__()
        self._step = step

    @override
    async def transform(self, input_: WrapperInputT, context: ExecutionContext) -> WrapperOutputT:
        wrapper_context = self.wrap(input_)
        return self.unwrap(await self._step.transform(wrapper_context.value, context), wrapper_context)

    @abstractmethod
    def wrap(self, input_: WrapperInputT) -> WrappingResult[StepInputT, WrappingContextT]:
        pass

    @abstractmethod
    def unwrap(
        self,
        input_: StepOutputT,
        wrapper_context: WrappingResult[StepInputT, WrappingContextT],
    ) -> WrapperOutputT:
        pass
