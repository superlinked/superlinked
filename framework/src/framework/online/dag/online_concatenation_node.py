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

from superlinked.framework.common.dag.concatenation_node import ConcatenationNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization.normalization import ConstantNorm
from superlinked.framework.common.util.collection_util import CollectionUtil
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType


class OnlineConcatenationNode(DefaultOnlineNode[ConcatenationNode, Vector], HasLength):
    def __init__(
        self,
        node: ConcatenationNode,
        parents: list[OnlineNode],
    ) -> None:
        super().__init__(node, parents, ParentValidationType.AT_LEAST_ONE_PARENT)
        self._norm = ConstantNorm(self.node.create_normalization_config([1.0] * len(self.node.parents)))

    @property
    def length(self) -> int:
        return self.node.length

    @override
    async def _evaluate_singles(
        self,
        parent_results: Sequence[dict[OnlineNode, SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> list[Vector | None]:
        self._check_evaluation_inputs(parent_results)
        vector_and_nodes_list: list[list[tuple[Vector, OnlineNode]]] = [
            [(result.value, parent) for parent, result in parent_result.items()] for parent_result in parent_results
        ]
        weighted_vectors = [
            self._apply_weights_and_concatenate(vector_and_nodes, context) for vector_and_nodes in vector_and_nodes_list
        ]
        return [self._norm.normalize(vector, context) for vector in weighted_vectors]

    def _apply_weights_and_concatenate(
        self,
        vector_and_nodes: Sequence[tuple[Vector, OnlineNode]],
        context: ExecutionContext,
    ) -> Vector:
        weighted_vectors = [vector * context.get_weight_of_node(parent.node_id) for vector, parent in vector_and_nodes]
        return CollectionUtil.concatenate_vectors(weighted_vectors)

    def _check_evaluation_inputs(
        self,
        parent_results: Sequence[dict[OnlineNode, SingleEvaluationResult]],
    ) -> None:
        if any(
            result
            for parent_result in parent_results
            for result in parent_result.values()
            if not isinstance(result.value, Vector)
        ):
            raise InvalidInputException(f"{self.class_name} can only process `Vector` inputs.")
