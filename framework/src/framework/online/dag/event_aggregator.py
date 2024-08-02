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

from dataclasses import dataclass
from datetime import timedelta

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.aggregation import Aggregation
from superlinked.framework.dsl.index.effect import EffectModifier


@dataclass
class EventMetadata:
    effect_count: int
    effect_avg_age: int
    oldest_effect_age: int


class EventAggregator:

    def __init__(self, context: ExecutionContext, aggregation: Aggregation) -> None:
        self._context = context
        self._aggregation = aggregation

    def calculate_event_vector(
        self,
        stored_result: Vector,
        affecting_vector: Vector,
        affecting_weight: float,
        event_metadata: EventMetadata,
        effect_modifier: EffectModifier,
    ) -> Vector:
        weighted_affecting_vector = Weighted(
            affecting_vector, affecting_weight * effect_modifier.temperature
        )
        weighted_stored_vector = Weighted(
            stored_result,
            self._calculate_stored_weight(
                self._context.now(), event_metadata, effect_modifier
            ),
        )
        return self._aggregation.aggregate_weighted(
            [weighted_affecting_vector, weighted_stored_vector], self._context
        )

    @classmethod
    def _calculate_stored_weight(
        cls,
        now: int,
        event_metadata: EventMetadata,
        effect_modifier: EffectModifier,
    ) -> float:
        return (
            cls._calculate_time_modifier(
                now,
                event_metadata.oldest_effect_age,
                event_metadata.effect_avg_age,
                effect_modifier.max_age,
            )
            * event_metadata.effect_count
            * (1 - effect_modifier.temperature)
        )

    @classmethod
    def _calculate_time_modifier(
        cls,
        now: int,
        oldest_effect_age: int,
        effect_avg_age: int,
        max_age: timedelta | None,
    ) -> float:
        if max_age and now == max_age.seconds:
            return 1.0
        lower_bound = now - max_age.seconds if max_age else oldest_effect_age
        if lower_bound >= effect_avg_age:
            return 0.0
        time_modifier = abs(effect_avg_age - lower_bound) / abs(now - lower_bound)
        return time_modifier
