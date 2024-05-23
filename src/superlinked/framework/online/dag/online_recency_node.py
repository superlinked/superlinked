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

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.recency_node import RecencyNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType

DAY_IN_SECONDS: int = 24 * 60 * 60


class OnlineRecencyNode(DefaultOnlineNode[RecencyNode, Vector], HasLength):
    def __init__(
        self,
        node: RecencyNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(
            node,
            parents,
            storage_manager,
            ParentValidationType.EXACTLY_ONE_PARENT,
        )

    @property
    def length(self) -> int:
        return self.node.embedding.length

    @override
    def _evaluate_singles(
        self,
        parent_results: list[dict[OnlineNode, SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> Sequence[Vector | None]:
        return [
            self._evaluate_single(parent_result, context)
            for parent_result in parent_results
        ]

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> Vector | None:
        if len(parent_results.items()) != 1:
            return None
        input_ = list(parent_results.values())[0]
        return self._calc_recency(input_.value, context)

    def _calc_recency(self, created_at: int, context: ExecutionContext) -> Vector:
        return self.node.embedding.calc_recency_vector(created_at, context)
