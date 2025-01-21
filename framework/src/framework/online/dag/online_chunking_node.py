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

from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.chunking_node import ChunkingNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.util.chunking_util import Chunker
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.exception import ChunkException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType


class OnlineChunkingNode(OnlineNode[ChunkingNode, str]):
    def __init__(
        self,
        node: ChunkingNode,
        parents: list[OnlineNode[Node[str], str]],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(
            node,
            parents,
            storage_manager,
            ParentValidationType.EXACTLY_ONE_PARENT,
        )

    def __chunk(
        self,
        text: str,
        chunk_size: int | None,
        chunk_overlap: int | None,
        split_chars_keep: list[str] | None = None,
        split_chars_remove: list[str] | None = None,
    ) -> list[str]:
        chunker = Chunker()
        return chunker.chunk_text(text, chunk_size, chunk_overlap, split_chars_keep, split_chars_remove)

    @override
    def evaluate_self(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[str] | None]:
        return [self.evaluate_self_single(schema, context) for schema in parsed_schemas]

    def evaluate_self_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[str] | None:
        parent_result = self.evaluate_parent(self.parents[0], [parsed_schema], context)[0]
        if parent_result is None:
            return None
        if len(parent_result.chunks) > 0:
            # We can just log a warning and proceed with input_.main.
            raise ChunkException(f"{self.class_name} cannot have a chunked input.")
        input_value = parent_result.main.value
        chunk_inputs = self.__chunk(
            input_value,
            self.node.chunk_size,
            self.node.chunk_overlap,
            self.node.split_chars_keep,
            self.node.split_chars_remove,
        )
        main = self._get_single_evaluation_result(input_value)
        chunks = [self._get_single_evaluation_result(chunk_input) for chunk_input in chunk_inputs]
        return EvaluationResult(main, chunks)
