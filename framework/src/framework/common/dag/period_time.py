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

from dataclasses import dataclass, field
from datetime import timedelta

from superlinked.framework.common.const import constants


@dataclass(frozen=True)
class PeriodTime:
    """
    A class representing a period time parameter.
    Attributes:
        period_time (timedelta): Oldest item the parameter will differentiate. Older items will have
            0 or `negative_filter` recency_score.
        weight (float): Defaults to 1.0. Useful to tune different period_times against each other.
    """

    period_time: timedelta = field(init=True)
    weight: float = field(default=constants.DEFAULT_WEIGHT, init=True)

    def __lt__(self, other: "PeriodTime") -> bool:
        if not isinstance(other, PeriodTime):
            return NotImplemented
        if self.period_time != other.period_time:
            return self.period_time < other.period_time
        return self.weight < other.weight

    def __post_init__(self) -> None:
        """
        Validate the PeriodTime after initialization.
        """
        if int(self.period_time.total_seconds()) <= 0:
            raise ValueError(
                f"Period_time parameter must be a positive time period, at least 1 seconds. "
                f"Got {self.period_time.__str__()} which is {int(self.period_time.total_seconds())} seconds."
            )
