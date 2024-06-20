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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.custom_embedding import CustomEmbedding
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import Aggregation


class CustomVectorEmbeddingNode(Node[Vector], HasLength, HasAggregation):
    def __init__(
        self,
        parent: Node[Vector],
        length: int,
        aggregation: Aggregation,
    ) -> None:
        super().__init__(Vector, [parent])
        self.__aggregation = aggregation
        self.embedding = CustomEmbedding(
            length=length, normalization=self.__aggregation.normalization
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
            "length": self.length,
            "aggregation": self.__aggregation,
        }
