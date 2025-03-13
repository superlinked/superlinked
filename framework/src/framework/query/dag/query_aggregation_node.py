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

from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.query.dag.exception import (
    QueryDagInitializationException,
    QueryEvaluationException,
)
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.dag.query_node_with_parent import QueryNodeWithParent


class QueryAggregationNode(QueryNodeWithParent[AggregationNode, Vector]):
    def __init__(self, node: AggregationNode, parents: Sequence[QueryNode[Node[Vector], Vector]]) -> None:
        super().__init__(node, parents)
        if len(self.parents) != 1:
            raise QueryDagInitializationException(f"{type(self).__name__} must have exactly 1 parent.")
        self.parent = self.parents[0]

    @override
    def _evaluate_parent_results(
        self,
        parent_results: Sequence[QueryEvaluationResult],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[Vector]:
        if len(parent_results) != 1:
            raise QueryEvaluationException(f"{type(self).__name__} can only evaluate exactly 1 parent result.")
        if not isinstance(parent_results[0].value, Vector):
            raise QueryEvaluationException(f"{type(self).__name__} can only evaluate vector type parent result.")
        return parent_results[0]

    @override
    def _validate_get_vector_parts_inputs(self, vectors: Sequence[Vector]) -> None:
        self._validate_vectors_dimension(self.node.length, vectors)

    @override
    def _get_vector_parts(
        self, vectors: Sequence[Vector], node_ids: Sequence[str], context: ExecutionContext
    ) -> list[list[Vector]] | None:
        return self.parent.get_vector_parts(vectors, node_ids, context)
