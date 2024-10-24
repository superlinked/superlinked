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

from abc import ABC, abstractmethod

from beartype.typing import Generic, Mapping, Sequence

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NT, NodeDataT
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryNode(ABC, Generic[NT, NodeDataT]):
    def __init__(self, node: NT, parents: Sequence[QueryNode]) -> None:
        super().__init__()
        self._node = node
        self.parents = parents

    @property
    def node(self) -> NT:
        return self._node

    @property
    def node_id(self) -> str:
        return self.node.node_id

    def evaluate_with_validation(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> NodeDataT:
        self._validate_evaluation_inputs(inputs)
        return self.evaluate(inputs, context)

    @abstractmethod
    def evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> NodeDataT:
        pass

    def _validate_evaluation_inputs(
        self, inputs: Mapping[str, Sequence[QueryNodeInput]]
    ) -> None:
        pass
