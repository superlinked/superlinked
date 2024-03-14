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

from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.util import time_util


class RecencyEmbedding(HasLength):
    def __init__(
        self,
        period_time_list: list[PeriodTime],
        negative_filter: float = 0,
    ) -> None:
        self.__period_time_list: list[PeriodTime] = period_time_list
        self.__negative_filter: float = float(negative_filter)
        self.__max_period_time: timedelta = max(
            param.period_time for param in self.__period_time_list
        )
        # a sin-cos pair for every period_time plus a dimension for negative filter or 0
        self.__length = len(period_time_list) * 2 + 1

    @property
    def length(self) -> int:
        return self.__length

    @property
    def negative_filter(self) -> float:
        return self.__negative_filter

    @property
    def max_period_time(self) -> timedelta:
        return self.__max_period_time

    @property
    def period_time_list(self) -> list[PeriodTime]:
        return self.__period_time_list

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

    def calc_recency_vector(
        self, created_at: int, time_period_start: int, is_query: bool
    ) -> Vector:
        return sum(
            (
                self.calc_recency_vector_for_period_time(
                    created_at,
                    period_time_param,
                    time_period_start,
                    is_query,
                )
                for period_time_param in self.__period_time_list
            ),
            Vector([]),
        )

    def calc_recency_vector_for_period_time(
        self,
        created_at: int,
        period_time: PeriodTime,
        time_period_start: int,
        is_query: bool,
    ) -> Vector:
        period_time_obj: float = period_time.period_time.total_seconds()
        full_circle_period_time: float = period_time_obj * 4

        time_elapsed: int = abs(created_at - self.__get_epoch())
        time_modulo: float = (
            time_elapsed % full_circle_period_time
        ) / full_circle_period_time
        x_value: float = math.cos(time_modulo * math.pi * 2) * period_time.weight
        y_value: float = math.sin(time_modulo * math.pi * 2) * period_time.weight
        z_value: float = 1.0 if is_query else 0

        out_of_time_scope = created_at < time_period_start - period_time_obj
        if out_of_time_scope:
            x_value = y_value = 0.0
            if period_time.period_time == self.__max_period_time:
                z_value = self.__negative_filter

        recency_vector: Vector = self.normalise_recency_vector(
            Vector([x_value, y_value])
        )
        if period_time.period_time == self.__max_period_time:
            recency_vector += Vector([z_value])

        return recency_vector

    def normalise_recency_vector(self, raw_recency_vector: Vector) -> Vector:
        return raw_recency_vector / math.sqrt(
            sum(period_time.weight**2 for period_time in self.__period_time_list)
        )
