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

from superlinked.framework.common.dag.comparison_filter_node import ComparisonFilterNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.exception import ParentCountException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineComparisonFilterNode(DefaultOnlineNode[ComparisonFilterNode, bool]):
    def __init__(
        self,
        node: ComparisonFilterNode,
        parent: OnlineNode,
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, [parent], evaluation_result_store_manager)

    @classmethod
    def from_node(
        cls,
        node: ComparisonFilterNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineComparisonFilterNode:
        if len(parents) != 1:
            raise ParentCountException(f"{cls.__name__} must have exactly 1 parent.")
        return cls(node, parents[0], evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[ComparisonFilterNode]:
        return ComparisonFilterNode

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> bool | None:
        if len(parent_results) != 1:
            raise ParentCountException(f"{self.class_name} must have exactly 1 parent.")
        parent_result: SingleEvaluationResult = list(parent_results.values())[0]
        return self.node.comparison_operation.evaluate(parent_result.value)
