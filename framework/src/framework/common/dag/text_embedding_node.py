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
from superlinked.framework.common.embedding.sentence_transformer_embedding import (
    SentenceTransformerEmbedding,
)
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    VectorAggregation,
)
from superlinked.framework.common.space.normalization import L2Norm


class TextEmbeddingNode(Node[Vector], HasLength, HasAggregation):
    def __init__(self, parent: Node[str], model_name: str, cache_size: int) -> None:
        super().__init__(Vector, [parent])
        self.model_name = model_name
        self.cache_size = cache_size
        self.__aggregation = VectorAggregation(L2Norm())
        self.post_init()

    def post_init(self) -> None:
        self.embedding = SentenceTransformerEmbedding(
            self.model_name, self.__aggregation.normalization, self.cache_size
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
            "model_name": self.model_name,
            "cache_size": self.cache_size,
            "aggregation": self.__aggregation,
        }
