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

from datetime import timedelta

from superlinked.framework.common.const import DEFAULT_WEIGHT


class PeriodTime:
    """
    A class representing a period time parameter.
    Attributes:
        period_time (timedelta): Oldest item the parameter will differentiate. Older items will have
            0 or `negative_filter` recency_score.
        weight (float): Defaults to 1.0. Useful to tune different period_times against each other.
    """

    def __init__(self, period_time: timedelta, weight: float = DEFAULT_WEIGHT) -> None:
        """
        Initialize the PeriodTime.
        Args:
            period_time (timedelta): Oldest item the parameter will differentiate.
                Older items will have 0 or `negative_filter` recency_score.
            weight (float, optional): Defaults to 1.0. Useful to tune different period_times against each other.
        """
        if int(period_time.total_seconds()) <= 0:
            raise ValueError(
                f"Period_time parameter must be a positive time period, at least 1 seconds. "
                f"Got {period_time.__str__()} which is {int(period_time.total_seconds())} seconds."
            )
        self.period_time = period_time
        self.weight = weight
