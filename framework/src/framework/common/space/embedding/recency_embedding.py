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
from superlinked.framework.common.util.collection_util import CollectionUtil

MAX_PERIOD_TIME_X_COORDINATE: int = -3
MAX_PERIOD_TIME_Y_COORDINATE: int = -2
EXPIRY_TIMEDELTA = timedelta(days=1)


class RecencyEmbedding(InvertibleEmbedding[int, RecencyEmbeddingConfig]):
    def __init__(self, embedding_config: RecencyEmbeddingConfig) -> None:
        super().__init__(embedding_config)
        # sort period times to ensure the last vector part corresponds to the max period_time
        self._period_time_list: Sequence[PeriodTime] = sorted(
            self._config.period_time_list, key=lambda x: x.period_time.total_seconds()
        )
        self._max_period_time = self._period_time_list[-1]

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @property
    def max_period_time(self) -> PeriodTime:
        return self._max_period_time

    @override
    def embed(self, input_: int, context: ExecutionContext) -> Vector:
        recency_vectors = [
            self.calc_recency_vector_for_period_time(input_, period_time_param, context)
            for period_time_param in self._period_time_list
        ]
        return CollectionUtil.concatenate_vectors(recency_vectors)

    @override
    def inverse_embed(self, vector: Vector, context: ExecutionContext) -> int:
        """
        This function might seem complex,
        but it essentially performs the inverse operation of the embed function.
        """
        x_value, y_value = (
            vector.value[MAX_PERIOD_TIME_X_COORDINATE],
            vector.value[MAX_PERIOD_TIME_Y_COORDINATE],
        )
        time_period_start = self._calculate_time_period_start(self.max_period_time, context.now())
        time_period_end: int = self._calculate_time_period_end(context.now())
        if (x_value == 0) and (y_value == 0):
            created_at = time_period_start - 1
            return created_at

        normalized_time_elapsed = math.atan2(y_value, x_value) * 2 / math.pi
        time_elapsed = round(normalized_time_elapsed * (time_period_end - time_period_start))
        return time_elapsed + time_period_start

    @property
    @override
    def needs_inversion_before_aggregation(self) -> bool:
        return True

    def calc_recency_vector_for_period_time(
        self, created_at: int, period_time: PeriodTime, context: ExecutionContext
    ) -> Vector:
        time_period_start: int = self._calculate_time_period_start(period_time, context.now())
        time_period_end: int = self._calculate_time_period_end(context.now())
        out_of_time_scope = not time_period_start <= created_at <= time_period_end
        z_value = self.calculate_z_value(period_time, context, out_of_time_scope)
        if out_of_time_scope:
            x_value = y_value = 0.0
        else:
            time_elapsed: int = created_at - time_period_start
            normalized_time_elapsed = time_elapsed / (time_period_end - time_period_start)
            x_value = math.cos(normalized_time_elapsed * math.pi / 2) * period_time.weight
            y_value = math.sin(normalized_time_elapsed * math.pi / 2) * period_time.weight

        return self._build_vector(x_value, y_value, z_value)

    def calculate_z_value(
        self,
        period_time: PeriodTime,
        context: ExecutionContext,
        out_of_time_scope: bool,
    ) -> float | None:
        if period_time.period_time == self.max_period_time.period_time:
            if context.is_query_context:
                z_value = 1.0
            elif out_of_time_scope:
                z_value = self._config.negative_filter
            else:
                z_value = 0.0
        else:
            z_value = None
        return z_value

    def _build_vector(self, x_value: float, y_value: float, z_value: float | None) -> Vector:
        vector_input = np.array([x_value, y_value])
        negative_filter_indices = set()
        if z_value is not None:
            vector_input = np.append(vector_input, np.array([z_value]))
            negative_filter_indices.add(2)
        return Vector(vector_input, negative_filter_indices)

    def _calculate_time_period_start(self, period_time: PeriodTime, now_ts: int) -> int:
        expiry_date = self.__get_expiry_date(now_ts)
        time_period_start = expiry_date - period_time.period_time + self._config.time_period_hour_offset
        utc_time_period_start = time_util.convert_datetime_to_utc_timestamp(time_period_start)
        return utc_time_period_start

    def _calculate_time_period_end(self, now_ts: int) -> int:
        """
        `EXPIRY_TIMEDELTA` later, dawn at `self._config.time_period_hour_offset` hour o'clock.
        """
        expiry_date = self.__get_expiry_date(now_ts)
        time_period_end = expiry_date + self._config.time_period_hour_offset
        utc_time_period_end = time_util.convert_datetime_to_utc_timestamp(time_period_end)
        return utc_time_period_end

    def __get_expiry_date(self, now_ts: int) -> datetime:
        now = time_util.convert_utc_timestamp_to_datetime(now_ts)
        now_only_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return now_only_day + EXPIRY_TIMEDELTA
