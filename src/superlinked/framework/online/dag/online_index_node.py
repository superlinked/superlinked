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

from beartype.typing import cast
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_concatenation_node import (
    OnlineConcatenationNode,
)
from superlinked.framework.online.dag.online_node import OnlineNode


class OnlineIndexNode(OnlineNode[IndexNode, Vector], HasLength):
    def __init__(
        self,
        node: IndexNode,
        parents: list[OnlineNode[Node[Vector], Vector]],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(node, parents, storage_manager)

    @property
    def length(self) -> int:
        return self.node.length

    def get_parent_for_schema(self, schema: SchemaObject) -> OnlineNode:
        active_parents = [
            parent
            for parent in self.parents
            if schema in cast(Node, parent.node).schemas
        ]
        if len(active_parents) != 1:
            raise ParentCountException(
                f"{self.class_name} must have exactly 1 parent per schema, got {len(active_parents)}"
            )
        return active_parents[0]

    def __get_parent_for_parsed_schemas(
        self, parsed_schemas: list[ParsedSchema]
    ) -> OnlineNode:
        active_parents = set(
            self.get_parent_for_schema(parsed_schema.schema)
            for parsed_schema in parsed_schemas
        )
        if len(active_parents) != 1:
            raise ParentCountException(
                f"{self.class_name} must have exactly 1 parent per schema, got {len(active_parents)}"
            )
        return cast(OnlineNode[Node[Vector], Vector], next(iter(active_parents)))

    @override
    def evaluate_self(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[Vector]]:
        parent: OnlineNode = self.__get_parent_for_parsed_schemas(parsed_schemas)
        parent_results: list[EvaluationResult[Vector]] = parent.evaluate_next(
            parsed_schemas, context
        )
        return [
            EvaluationResult(
                self._get_single_evaluation_result(parent_result.main.value),
                [
                    self._get_single_evaluation_result(chunk_result.value)
                    for chunk_result in parent_result.chunks
                ],
            )
            for parent_result in parent_results
        ]

    def _re_weight_vector(
        self,
        schema: SchemaObject,
        vector: Vector,
        context: ExecutionContext,
    ) -> Vector:
        online_parent_node = self.get_parent_for_schema(schema)
        if isinstance(online_parent_node, OnlineConcatenationNode):
            return online_parent_node.re_weight_vector(vector, context)
        return vector
