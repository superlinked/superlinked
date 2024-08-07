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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.number_embedding import (
    Mode,
    NumberEmbedding,
    Scale,
)
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    InputAggregation,
    InputAggregationMode,
)
from superlinked.framework.common.space.normalization import NoNorm


@dataclass
class NumberEmbeddingParams:
    min_value: float
    max_value: float
    mode: Mode
    scale: Scale
    negative_filter: float


class NumberEmbeddingNode(Node[Vector], HasLength, HasAggregation):
    def __init__(
        self,
        parent: Node[float] | Node[int],
        embedding_params: NumberEmbeddingParams,
        aggregation_mode: InputAggregationMode,
    ) -> None:
        super().__init__(Vector, [parent])
        normalization = NoNorm()
        self.embedding = NumberEmbedding(
            embedding_params.min_value,
            embedding_params.max_value,
            embedding_params.mode,
            embedding_params.scale,
            embedding_params.negative_filter,
            normalization,
        )
        self.__aggregation: InputAggregation = InputAggregation.from_aggregation_mode(
            aggregation_mode, normalization, self.embedding
        )
        self.mode = embedding_params.mode

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
            "min_value": self.embedding._min_value,
            "max_value": self.embedding._max_value,
            "mode": self.embedding._mode,
            "scale": self.embedding._scale,
            "negative_filter": self.embedding._negative_filter,
            "aggregation": self.__aggregation,
        }
