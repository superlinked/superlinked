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

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.sentence_transformer_embedding import (
    SentenceTransformerEmbedding,
)
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization


class TextEmbeddingNode(Node[Vector], HasLength):
    def __init__(
        self, parent: Node[str], model_name: str, normalization: Normalization
    ) -> None:
        super().__init__([parent])
        self.model_name = model_name
        self.__normalization = normalization
        self.post_init()
        super().__init__([parent])

    def post_init(self) -> None:
        self.embedding = SentenceTransformerEmbedding(
            self.model_name, self.__normalization
        )

    @property
    def length(self) -> int:
        return self.embedding.length

    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {"model_name": self.model_name, "normalization": self.__normalization}
