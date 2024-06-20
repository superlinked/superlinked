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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.recency_embedding import (
    RecencyEmbedding,
    calculate_recency_normalization,
)
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    InputAggregation,
    InputAggregationMode,
)


class RecencyNode(Node[Vector], HasLength, HasAggregation):
    def __init__(
        self,
        parent: Node[int],
        time_period_hour_offset: timedelta,
        period_time_list: list[PeriodTime],
        aggregation_mode: InputAggregationMode,
        negative_filter: float,
    ) -> None:
        super().__init__(Vector, [parent])
        normalization = calculate_recency_normalization(period_time_list)
        self.embedding = RecencyEmbedding(
            period_time_list,
            normalization,
            time_period_hour_offset,
            negative_filter,
        )
        self.__aggregation: InputAggregation = InputAggregation.from_aggregation_mode(
            aggregation_mode, normalization, self.embedding
        )

    @property
    def length(self) -> int:
        return self.embedding.length

    @property
    @override
    def aggregation(self) -> Aggregation:
        return self.__aggregation

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "period_time_list": self.embedding.period_time_list,
            "negative_filter": self.embedding.negative_filter,
            "aggregation": self.__aggregation,
        }
