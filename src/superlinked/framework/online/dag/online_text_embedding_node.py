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

from __future__ import annotations

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.text_embedding_node import TextEmbeddingNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineTextEmbeddingNode(DefaultOnlineNode[TextEmbeddingNode, Vector], HasLength):
    def __init__(
        self,
        node: TextEmbeddingNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, parents, evaluation_result_store_manager)

    @property
    def length(self) -> int:
        return self.node.length

    @classmethod
    def from_node(
        cls,
        node: TextEmbeddingNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineTextEmbeddingNode:
        return cls(node, parents, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[TextEmbeddingNode]:
        return TextEmbeddingNode

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> Vector | None:
        if len(parent_results.items()) != 1:
            return None
        input_ = list(parent_results.values())[0]
        return self.__embed_text(input_.value).normalize()

    def __embed_text(self, text: str) -> Vector:
        return self.node.embedding.transform(text)
