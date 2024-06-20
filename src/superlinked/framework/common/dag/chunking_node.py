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


class ChunkingNode(Node[str]):
    def __init__(
        self,
        parent: Node[str],
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        split_chars_keep: list[str] | None = None,
        split_chars_remove: list[str] | None = None,
    ) -> None:
        super().__init__(str, [parent])
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.split_chars_keep = split_chars_keep
        self.split_chars_remove = split_chars_remove

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "split_chars_keep": self.split_chars_keep,
            "split_chars_remove": self.split_chars_remove,
        }
