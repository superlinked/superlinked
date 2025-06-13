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

from beartype.typing import Mapping, Sequence
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.recency_node import RecencyNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.query.dag.query_embedding_orphan_node import (
    QueryEmbeddingOrphanNode,
)
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import (
    QueryNodeInput,
    QueryNodeInputValue,
)


class QueryRecencyNode(QueryEmbeddingOrphanNode[int, RecencyNode, int]):
    def __init__(self, node: RecencyNode, parents: Sequence[QueryNode]) -> None:
        super().__init__(node, parents, int)

    @override
    async def _evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[Vector]:
        return await super()._evaluate(
            self._merge_inputs(
                [
                    inputs,
                    {
                        self.node_id: [
                            QueryNodeInput(QueryNodeInputValue(context.now(), constants.DEFAULT_WEIGHT), False)
                        ]
                    },
                ]
            ),
            context,
        )
