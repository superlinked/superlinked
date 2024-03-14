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

from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NDT
from superlinked.framework.common.exception import InitializationException
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineConstantNode(DefaultOnlineNode[ConstantNode[NDT], NDT]):
    def __init__(
        self,
        node: ConstantNode,
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, [], evaluation_result_store_manager)

    @classmethod
    def from_node(
        cls,
        node: ConstantNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineConstantNode:
        if len(parents) != 0:
            raise InitializationException(f"{cls.__name__} cannot have parents.")
        return cls(node, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[ConstantNode]:
        return ConstantNode

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> NDT | None:
        return self.node.value
