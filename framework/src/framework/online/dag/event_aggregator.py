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
from superlinked.framework.common.dag.effect_modifier import EffectModifier
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)

WARP = 0.2  # ensures that the time modifier does not become too extreme, cannot be 1.0


@dataclass
class EventMetadata:
    effect_count: int
    effect_avg_ts: int
    effect_oldest_ts: int


@dataclass
class EventAggregatorParams:
    context: ExecutionContext
    stored_result: Vector
    affecting_vector: Weighted[Vector]
    event_metadata: EventMetadata
    effect_modifier: EffectModifier
    transformation_config: TransformationConfig


class EventAggregator:
    def __init__(self, params: EventAggregatorParams) -> None:
        self._params = params
        self._aggregation_transformation = (
            TransformationFactory.create_aggregation_transformation(
                self._params.transformation_config
            )
        )

    def calculate_event_vector(self) -> Vector:
        weighted_affecting_vector = Weighted(
            self._params.affecting_vector.item,
            self._params.affecting_vector.weight
            * self._params.effect_modifier.temperature,
        )
        weighted_stored_vector = Weighted(
            self._params.stored_result, self._calculate_stored_weight()
        )
        not_empty_weighted_vectors = [
            weighted_vector
            for weighted_vector in [weighted_affecting_vector, weighted_stored_vector]
            if not weighted_vector.item.is_empty
        ]
        return self._aggregation_transformation.transform(
            not_empty_weighted_vectors,
            self._params.context,
        )

    def _calculate_stored_weight(self) -> float:
        return (
            EventAggregator._calculate_time_modifier(
                self._params.context.now(),
                self._params.event_metadata.effect_oldest_ts,
                self._params.event_metadata.effect_avg_ts,
                self._params.effect_modifier.max_age_delta,
            )
            * self._params.event_metadata.effect_count
            * (1 - self._params.effect_modifier.temperature)
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
        if max_age_delta_seconds == 0:
            return 1.0
        avg_effect_delta = now - effect_avg_ts
        if max_age_delta_seconds < avg_effect_delta:
            return 0.0
        normalized_age = avg_effect_delta / max_age_delta_seconds
        time_modifier = (1 - normalized_age) * (1 - WARP) + WARP
        return time_modifier
