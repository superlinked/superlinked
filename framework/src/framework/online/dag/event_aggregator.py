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

from beartype.typing import Sequence

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.effect_modifier import EffectModifier
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.config.normalization.normalization_config import (
    NoNormConfig,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.space.embedding.model_based.singleton_embedding_engine_manager import (
    SingletonEmbeddingEngineManager,
)
from superlinked.framework.common.space.normalization.normalization import L1Norm
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.online.dag.event_metadata_handler import EventMetadata


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
        # * We cannot normalize, as normalization will skew the event vector.
        transform_config_with_no_norm = TransformationConfig(
            NoNormConfig(),
            self._params.transformation_config.aggregation_config,
            self._params.transformation_config.embedding_config,
        )
        self._aggregation_transformation = TransformationFactory.create_aggregation_transformation(
            transform_config_with_no_norm, SingletonEmbeddingEngineManager()
        )

    async def calculate_event_vector(self) -> Vector:
        weighted_affecting_vector = Weighted(
            self._params.affecting_vector.item,
            self._params.affecting_vector.weight,
        )
        aggregated_affecting_vector = await self._aggregation_transformation.transform(
            [weighted_affecting_vector],
            self._params.context,
        )
        weighted_affecting_vector = Weighted(
            aggregated_affecting_vector,
            self._params.effect_modifier.temperature,
        )
        weighted_stored_vector = Weighted(self._params.stored_result, self._calculate_stored_weight())
        not_empty_weighted_vectors = [
            weighted_vector
            for weighted_vector in [weighted_affecting_vector, weighted_stored_vector]
            if not weighted_vector.item.is_empty
        ]
        normalized_weighted_vectors = self.calculate_normalized_weighted_vectors(not_empty_weighted_vectors)
        return await self._aggregation_transformation.transform(
            normalized_weighted_vectors,
            self._params.context,
        )

    def calculate_normalized_weighted_vectors(
        self, not_empty_weighted_vectors: Sequence[Weighted[Vector]]
    ) -> Sequence[Weighted[Vector]]:
        # * We have to normalize the weight as we want to avoid L2 norm on the result vector.
        weights = [v.weight for v in not_empty_weighted_vectors]
        normalized_weights = L1Norm().normalize(Vector(weights)).value
        return [Weighted(vector.item, normalized_weights[i]) for i, vector in enumerate(not_empty_weighted_vectors)]

    def _calculate_stored_weight(self) -> float:
        return (
            EventAggregator._calculate_time_modifier(
                self._params.context.now(),
                self._params.event_metadata.effect_oldest_ts,
                self._params.event_metadata.effect_avg_ts,
                self._params.effect_modifier.max_age_delta,
                self._params.effect_modifier.time_decay_floor,
            )
            * (self._params.event_metadata.effect_count - 1)
            * (1 - self._params.effect_modifier.temperature)
        )

    @classmethod
    def _calculate_time_modifier(
        cls,
        now: int,
        effect_oldest_ts: int,
        effect_avg_ts: int,
        max_age_delta: timedelta | None,
        time_decay_floor: float,
    ) -> float:
        max_age_delta_seconds = int(max_age_delta.total_seconds()) if max_age_delta else now - effect_oldest_ts
        if max_age_delta_seconds == 0:
            return 1.0
        avg_effect_delta = now - effect_avg_ts
        if max_age_delta_seconds < avg_effect_delta:
            return 0.0
        normalized_age = avg_effect_delta / max_age_delta_seconds
        time_modifier = (1 - normalized_age) * (1 - time_decay_floor) + time_decay_floor
        return time_modifier
