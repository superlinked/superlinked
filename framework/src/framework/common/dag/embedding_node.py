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


from abc import abstractmethod
from dataclasses import asdict

from beartype.typing import Any, Generic
from typing_extensions import override

from superlinked.framework.common.dag.node import Node, NodeDataT
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding, EmbeddingConfigT
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    InputAggregation,
    InputAggregationMode,
    VectorAggregation,
)


class EmbeddingNode(Generic[NodeDataT, EmbeddingConfigT], Node[Vector], HasLength):
    def __init__(
        self,
        parent: Node[NodeDataT],
        embedding_config: EmbeddingConfigT,
        aggregation: Aggregation,
    ) -> None:
        super().__init__(Vector, [parent])
        self._embedding_config = embedding_config
        self._aggregation = aggregation

    @property
    @abstractmethod
    def embedding_type(self) -> type[Embedding[NodeDataT, EmbeddingConfigT]]:
        pass

    @property
    @override
    def length(self) -> int:
        return self._embedding_config.length

    @property
    def embedding_config(self) -> EmbeddingConfigT:
        return self._embedding_config

    @property
    def aggregation(self) -> Aggregation:
        return self._aggregation

    def init_embedding(self) -> Embedding[NodeDataT, EmbeddingConfigT]:
        return self.embedding_type(self.embedding_config)

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "embedding_config": str(asdict(self.embedding_config)),
            "aggregation": type(self.aggregation).__name__,
        }


class VectorEmbeddingNode(
    Generic[NodeDataT, EmbeddingConfigT], EmbeddingNode[NodeDataT, EmbeddingConfigT]
):
    def __init__(
        self, parent: Node[NodeDataT], embedding_config: EmbeddingConfigT
    ) -> None:
        aggregation = VectorAggregation()
        super().__init__(parent, embedding_config, aggregation)


class InputEmbeddingNode(
    Generic[NodeDataT, EmbeddingConfigT], EmbeddingNode[NodeDataT, EmbeddingConfigT]
):
    def __init__(
        self,
        parent: Node[NodeDataT],
        embedding_config: EmbeddingConfigT,
        aggregation_mode: InputAggregationMode,
    ) -> None:
        aggregation = InputAggregation.from_aggregation_mode(aggregation_mode)
        super().__init__(parent, embedding_config, aggregation)
