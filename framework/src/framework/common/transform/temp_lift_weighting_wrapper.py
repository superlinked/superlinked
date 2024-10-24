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

from beartype.typing import Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.transform.transform import (
    StepInputT,
    StepOutputT,
    WrapperStep,
    WrappingResult,
)


class TempLiftWeightingWrapper(
    Generic[StepInputT, StepOutputT],
    WrapperStep[
        Sequence[Weighted[StepInputT]],
        Sequence[Weighted[StepOutputT]],
        Sequence[float],
        Sequence[StepInputT],
        Sequence[StepOutputT],
    ],
):
    @override
    def wrap(
        self, input_: Sequence[Weighted[StepInputT]]
    ) -> WrappingResult[Sequence[StepInputT], Sequence[float]]:
        items = [item.item for item in input_]
        weights = [item.weight for item in input_]
        return WrappingResult(items, weights)

    @override
    def unwrap(
        self,
        input_: Sequence[StepOutputT],
        wrapper_context: WrappingResult[Sequence[StepInputT], Sequence[float]],
    ) -> Sequence[Weighted[StepOutputT]]:
        if len(input_) != len(wrapper_context.context):
            raise ValueError(
                f"Mismatching input {len(input_)} and output {len(wrapper_context.context)} counts"
            )
        return [
            Weighted(item, weight)
            for item, weight in zip(input_, wrapper_context.context)
        ]
