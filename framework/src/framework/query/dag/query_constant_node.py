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

from beartype.typing import Generic, Mapping, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NodeDataT
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryConstantNode(QueryNode[ConstantNode[NodeDataT], NodeDataT], Generic[NodeDataT]):
    def __init__(
        self,
        node: ConstantNode[NodeDataT],
        parents: Sequence[QueryNode],
    ) -> None:
        super().__init__(node, parents)

    @override
    async def _evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[NodeDataT]:
        return QueryEvaluationResult(self.node.value)
