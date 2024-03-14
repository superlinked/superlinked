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

from typing import cast

from typing_extensions import override

from superlinked.framework.common.dag.chunking_node import ChunkingNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.embedding.chunking_util import Chunker
from superlinked.framework.common.exception import (
    DagEvaluationException,
    InitializationException,
)
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.exception import ChunkException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineChunkingNode(OnlineNode[ChunkingNode, str]):
    def __init__(
        self,
        node: ChunkingNode,
        parent: OnlineNode[Node[str], str],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, [parent], evaluation_result_store_manager)

    @classmethod
    def from_node(
        cls,
        node: ChunkingNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineChunkingNode:
        if len(parents) != 1:
            raise InitializationException(f"{cls.__name__} must have exactly 1 parent.")
        return cls(node, parents[0], evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[ChunkingNode]:
        return ChunkingNode

    def __chunk(
        self, text: str, chunk_size: int | None, chunk_overlap: int | None
    ) -> list[str]:
        chunker = Chunker()
        return chunker.chunk_text(text, chunk_size, chunk_overlap)

    @override
    def evaluate_self(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[str]:
        if len(self.parents) != 1:
            stored_result = self.load_stored_result(
                parsed_schema.id_, parsed_schema.schema
            )
            if stored_result is None:
                raise DagEvaluationException(
                    f"{self.class_name} doesn't have a stored result."
                )
            return EvaluationResult(self._get_single_evaluation_result(stored_result))
        input_: EvaluationResult[str] = cast(
            OnlineNode[Node[str], str], self.parents[0]
        ).evaluate_next(parsed_schema, context)
        if len(input_.chunks) > 0:
            # We can just log a warning and proceed with input_.main.
            raise ChunkException(f"{self.class_name} cannot have a chunked input.")
        input_value = input_.main.value
        chunk_inputs = self.__chunk(
            input_value, self.node.chunk_size, self.node.chunk_overlap
        )
        main = self._get_single_evaluation_result(input_value)
        chunks = [
            self._get_single_evaluation_result(chunk_input)
            for chunk_input in chunk_inputs
        ]
        return EvaluationResult(main, chunks)
