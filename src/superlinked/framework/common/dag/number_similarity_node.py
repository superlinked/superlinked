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

from typing import Any

from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.number_similarity_embedding import (
    NumberSimilarityEmbedding,
)
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    InputAggregationMode,
    get_input_aggregation,
)
from superlinked.framework.common.space.normalization import NoNorm


class NumberSimilarityNode(Node[Vector], HasLength, HasAggregation):
    def __init__(
        self,
        parent: Node[float | int],
        min_value: float,
        max_value: float,
        negative_filter: float,
        aggregation_mode: InputAggregationMode,
    ) -> None:
        super().__init__([parent])
        normalization = NoNorm()
        self.embedding = NumberSimilarityEmbedding(
            min_value,
            max_value,
            negative_filter,
            normalization,
        )
        self.__aggregation = get_input_aggregation(
            aggregation_mode, normalization, self.embedding
        )

    @property
    def length(self) -> int:
        return self.embedding.length

    @property
    @override
    def aggregation(self) -> Aggregation:
        return self.__aggregation

    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "min_value": self.embedding._min_value,
            "max_value": self.embedding._max_value,
            "negative_filter": self.embedding._negative_filter,
            "aggregation": self.__aggregation,
        }
