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

WARP = 0.2  # ensures that the time modifier does not become too extreme, cannot be 1.0


@dataclass
class EventMetadata:
    effect_count: int
    effect_avg_ts: int
    effect_oldest_ts: int


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
                event_metadata.effect_oldest_ts,
                event_metadata.effect_avg_ts,
                effect_modifier.max_age_delta,
            )
            * event_metadata.effect_count
            * (1 - effect_modifier.temperature)
        )

    @classmethod
    def _calculate_time_modifier(
        cls,
        now: int,
        effect_oldest_ts: int,
        effect_avg_ts: int,
        max_age_delta: timedelta | None,
    ) -> float:
        max_age_delta_seconds = (
            int(max_age_delta.total_seconds())
            if max_age_delta
            else now - effect_oldest_ts
        )
        avg_effect_delta = now - effect_avg_ts
        if max_age_delta_seconds < avg_effect_delta:
            return 0.0
        normalized_age = avg_effect_delta / max_age_delta_seconds
        time_modifier = (1 - normalized_age) * (1 - WARP) + WARP
        return time_modifier
