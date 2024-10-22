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

from dataclasses import dataclass
from datetime import timedelta

import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)

logger = structlog.getLogger()


@dataclass(frozen=True)
class RecencyEmbeddingConfig(EmbeddingConfig[int]):
    period_time_list: Sequence[PeriodTime]
    time_period_hour_offset: timedelta
    negative_filter: float = 0.0

    def __post_init__(
        self,
    ) -> None:
        self._validate_input()

    def _validate_input(self) -> None:
        if self.negative_filter > 0:
            sum_weights: float = sum(param.weight for param in self.period_time_list)

            max_period_time: timedelta = max(
                param.period_time for param in self.period_time_list
            )
            max_period_time_str = (
                f"{max_period_time.days} days"
                if max_period_time.days
                else f"{round(max_period_time.total_seconds() / 3600, 2)} hours"
            )
            logger.warning(
                "Positive negative_filter value was supplied. This will lead to "
                "old items (older than max_period_time) having recency scores of "
                "negative_filter.\nMeanwhile the largest recency score possible for the most "
                "recent items is around the sum of weights, and the score at max_period_time will be 0. "
                "\nUse with caution.",
                negative_filter=self.negative_filter,
                max_period_time=max_period_time_str,
                sum_of_weights=sum_weights,
            )

        if any(param.weight < 0 for param in self.period_time_list):
            logger.warning(
                "Negative weight was supplied for some period_time_param. This can lead to very strange "
                "recency score curves. Use with caution. \n"
                "To better understand your recency scores use RecencyPlotter."
                "It can be imported from `superlinked.evaluation.charts.recency_plotter`. \n"
                "Check an example notebook at: https://github.com/superlinked/superlinked/blob/main"
                "/notebook/combining_recency_and_relevance.ipynb. "
            )
        if self.time_period_hour_offset >= timedelta(hours=24):
            raise ValueError("Time period hour offset must be less than a day.")

    @property
    @override
    def length(self) -> int:
        # a sin-cos pair for every period_time plus a dimension for negative filter or 0
        return len(self.period_time_list) * 2 + 1
