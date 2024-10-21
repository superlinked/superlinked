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

import math
from datetime import datetime, timedelta
from functools import reduce

import numpy as np
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.recency_embedding_config import (
    RecencyEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.embedding import InvertibleEmbedding
from superlinked.framework.common.util import time_util

MAX_PERIOD_TIME_X_COORDINATE: int = -3
MAX_PERIOD_TIME_Y_COORDINATE: int = -2


class RecencyEmbedding(InvertibleEmbedding[int, RecencyEmbeddingConfig]):
    def __init__(self, embedding_config: RecencyEmbeddingConfig) -> None:
        super().__init__(embedding_config)
        # sort period times to ensure the last vector part corresponds to the max period_time
        self._period_time_list: Sequence[PeriodTime] = sorted(
            self._config.period_time_list, key=lambda x: x.period_time.total_seconds()
        )
        self._max_period_time: PeriodTime = max(
            self._period_time_list, key=lambda p: p.period_time
        )
        self._epoch = self._get_epoch()

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @property
    def max_period_time(self) -> PeriodTime:
        return self._max_period_time

    @override
    def embed(self, input_: int, context: ExecutionContext) -> Vector:
        return reduce(
            lambda a, b: a.concatenate(b),
            (
                self.calc_recency_vector_for_period_time(
                    input_,
                    period_time_param,
                    context,
                )
                for period_time_param in self._period_time_list
            ),
        )

    @override
    def inverse_embed(self, vector: Vector, context: ExecutionContext) -> int:
        """
        This function might seem complex,
        but it essentially performs the inverse operation of the embed function.
        """
        time_period_start = self._calculate_time_period_start(context)
        period_time_in_secs: float = self._max_period_time.period_time.total_seconds()
        full_circle_period_time: float = period_time_in_secs * 4

        x_value, y_value = (
            vector.value[MAX_PERIOD_TIME_X_COORDINATE],
            vector.value[MAX_PERIOD_TIME_Y_COORDINATE],
        )

        if (x_value == 0) and (y_value == 0):
            created_at = time_period_start - period_time_in_secs - 1
            return int(created_at)

        time_modulo = math.atan2(
            y_value / self._max_period_time.weight,
            x_value / self._max_period_time.weight,
        ) / (2 * math.pi)
        time_elapsed = abs(time_modulo) * full_circle_period_time
        created_at = time_period_start + period_time_in_secs - time_elapsed
        return int(created_at)

    @property
    @override
    def needs_inversion_before_aggregation(self) -> bool:
        return True

    def calc_recency_vector_for_period_time(
        self,
        created_at: int,
        period_time: PeriodTime,
        context: ExecutionContext,
    ) -> Vector:
        time_period_start: int = self._calculate_time_period_start(context)
        created_at_constrained: int = min(created_at, time_period_start)
        period_time_in_secs: float = period_time.period_time.total_seconds()
        full_circle_period_time: float = period_time_in_secs * 4

        time_elapsed: int = abs(created_at_constrained - self._epoch)
        time_modulo: float = (
            time_elapsed % full_circle_period_time
        ) / full_circle_period_time

        out_of_time_scope = (
            created_at_constrained < time_period_start - period_time_in_secs
        )

        z_value = self.calculate_z_value(period_time, context, out_of_time_scope)
        if out_of_time_scope:
            x_value = y_value = 0.0
        else:
            x_value = math.cos(time_modulo * math.pi * 2) * period_time.weight
            y_value = math.sin(time_modulo * math.pi * 2) * period_time.weight

        recency_vector = self._build_vector(x_value, y_value, z_value)
        return recency_vector

    def calculate_z_value(
        self,
        period_time: PeriodTime,
        context: ExecutionContext,
        out_of_time_scope: bool,
    ) -> float | None:
        if period_time.period_time == self._max_period_time.period_time:
            if context.is_query_context:
                z_value = 1.0
            elif out_of_time_scope:
                z_value = float(self._config.negative_filter)
            else:
                z_value = 0.0
        else:
            z_value = None
        return z_value

    def _build_vector(
        self, x_value: float, y_value: float, z_value: float | None
    ) -> Vector:
        vector_input = np.array([x_value, y_value])
        negative_filter_indices = set()
        if z_value is not None:
            vector_input = np.append(vector_input, np.array([z_value]))
            negative_filter_indices.add(2)
        return Vector(vector_input, negative_filter_indices)

    def _calculate_time_period_start(
        self,
        context: ExecutionContext,
    ) -> int:
        now = datetime.fromtimestamp(context.now())
        now_only_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = now_only_day + timedelta(days=1)
        time_period_start = next_day + self._config.time_period_hour_offset
        utc_time_period_start = time_util.convert_datetime_to_utc_timestamp(
            time_period_start
        )
        return utc_time_period_start

    @staticmethod
    def _get_epoch() -> int:
        """
        Earliest possible python datetime. Cannot make this work for earlier dates than epoch.
        This is needed to provide a base for recency calculations.
        All timestamps are evaluated based on distance (phase actually) to this timestamp with respect to period times.
        """
        epoch: int = time_util.convert_datetime_to_utc_timestamp(
            datetime(year=1753, month=1, day=1, hour=0, minute=0, second=0)
        )
        return epoch
