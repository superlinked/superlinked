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
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import ConstantNorm, Normalization
from superlinked.framework.common.util import time_util

MAX_PERIOD_TIME_X_COORDINATE: int = -3
MAX_PERIOD_TIME_Y_COORDINATE: int = -2


class RecencyEmbedding(Embedding[int], HasLength):
    def __init__(
        self,
        period_time_list: list[PeriodTime],
        normalization: Normalization,
        time_period_hour_offset: timedelta,
        negative_filter: float = 0.0,
    ) -> None:
        # sort period times to ensure the last vector part corresponds to the max period_time
        self.__period_time_list: list[PeriodTime] = sorted(
            period_time_list, key=lambda x: x.period_time.total_seconds()
        )
        self.__negative_filter: float = float(negative_filter)
        self.__max_period_time: PeriodTime = max(
            self.__period_time_list, key=lambda p: p.period_time
        )
        self.__normalization = normalization
        # a sin-cos pair for every period_time plus a dimension for negative filter or 0
        self.__length = len(period_time_list) * 2 + 1
        self.__time_period_hour_offset: timedelta = time_period_hour_offset
        self.__validate_time_period_hour_offset()

    def __validate_time_period_hour_offset(self) -> None:
        if self.__time_period_hour_offset >= timedelta(hours=24):
            raise InitializationException(
                "Time period hour offset must be less than a day."
            )

    @property
    def length(self) -> int:
        return self.__length

    @property
    def negative_filter(self) -> float:
        return self.__negative_filter

    @property
    def max_period_time(self) -> PeriodTime:
        return self.__max_period_time

    @property
    def time_period_hour_offset(self) -> timedelta:
        return self.__time_period_hour_offset

    @property
    def period_time_list(self) -> list[PeriodTime]:
        return self.__period_time_list

    @property
    def normalization(self) -> Normalization:
        return self.__normalization

    @staticmethod
    def __get_epoch() -> int:
        """
        Earliest possible python datetime. Cannot make this work for earlier dates than epoch.
        This is needed to provide a base for recency calculations.
        All timestamps are evaluated based on distance (phase actually) to this timestamp with respect to period times.
        """
        epoch: int = time_util.convert_datetime_to_utc_timestamp(
            datetime(year=1753, month=1, day=1, hour=0, minute=0, second=0)
        )
        return epoch

    @property
    def epoch(self) -> int:
        return self.__get_epoch()

    @override
    def embed(self, input_: int, context: ExecutionContext) -> Vector:
        return self.calc_recency_vector(input_, context)

    @override
    def inverse_embed(self, vector: Vector, context: ExecutionContext) -> int:
        """
        This function might seem complex,
        but it essentially performs the inverse operation of the embed function.
        """
        time_period_start = self.__calculate_time_period_start(context)
        denormalized = self.__normalization.denormalize(vector)
        period_time_in_secs: float = self.max_period_time.period_time.total_seconds()
        full_circle_period_time: float = period_time_in_secs * 4

        x_value, y_value = (
            denormalized.value[MAX_PERIOD_TIME_X_COORDINATE],
            denormalized.value[MAX_PERIOD_TIME_Y_COORDINATE],
        )

        if (x_value == 0) and (y_value == 0):
            created_at = time_period_start - period_time_in_secs - 1
            return int(created_at)

        time_modulo = math.atan2(
            y_value / self.max_period_time.weight, x_value / self.max_period_time.weight
        ) / (2 * math.pi)
        time_elapsed = abs(time_modulo) * full_circle_period_time
        created_at = time_period_start + period_time_in_secs - time_elapsed
        return int(created_at)

    def calc_recency_vector(self, created_at: int, context: ExecutionContext) -> Vector:
        return reduce(
            lambda a, b: a.concatenate(b),
            (
                self.calc_recency_vector_for_period_time(
                    created_at,
                    period_time_param,
                    context,
                )
                for period_time_param in self.__period_time_list
            ),
        )

    def calc_recency_vector_for_period_time(
        self,
        created_at: int,
        period_time: PeriodTime,
        context: ExecutionContext,
    ) -> Vector:
        time_period_start: int = self.__calculate_time_period_start(context)
        created_at_constrained: int = min(created_at, time_period_start)
        period_time_in_secs: float = period_time.period_time.total_seconds()
        full_circle_period_time: float = period_time_in_secs * 4

        time_elapsed: int = abs(created_at_constrained - self.epoch)
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
        if period_time.period_time == self.__max_period_time.period_time:
            if context.is_query_context:
                z_value = 1.0
            elif out_of_time_scope:
                z_value = self.__negative_filter
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
        recency_vector: Vector = Vector(vector_input, negative_filter_indices)
        return self.__normalization.normalize(recency_vector)

    def __calculate_time_period_start(
        self,
        context: ExecutionContext,
    ) -> int:
        now = datetime.fromtimestamp(context.now())
        now_only_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = now_only_day + timedelta(days=1)
        time_period_start = next_day + self.__time_period_hour_offset
        utc_time_period_start = time_util.convert_datetime_to_utc_timestamp(
            time_period_start
        )
        return utc_time_period_start


def calculate_recency_normalization(period_time_list: list[PeriodTime]) -> ConstantNorm:
    return ConstantNorm(
        math.sqrt(sum(period_time.weight**2 for period_time in period_time_list))
    )
