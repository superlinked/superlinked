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

from functools import reduce

from beartype.typing import Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.concatenation_node import ConcatenationNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization.normalization import L2Norm
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.util.weight_arithmetics import WeightArithmetics
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType


class OnlineConcatenationNode(DefaultOnlineNode[ConcatenationNode, Vector], HasLength):
    def __init__(
        self,
        node: ConcatenationNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(
            node, parents, storage_manager, ParentValidationType.AT_LEAST_ONE_PARENT
        )
        self._norm = L2Norm()

    @property
    def length(self) -> int:
        return self.node.length

    @override
    def _evaluate_singles(
        self,
        parent_results: list[dict[OnlineNode, SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> Sequence[Vector | None]:
        self._check_evaluation_inputs(parent_results)
        vector_and_nodes_list: list[list[tuple[Vector, OnlineNode]]] = [
            [(result.value, parent) for parent, result in parent_result.items()]
            for parent_result in parent_results
        ]
        weighted_vectors = [
            self._apply_weights_and_concatenate(vector_and_nodes, context)
            for vector_and_nodes in vector_and_nodes_list
        ]
        if not context.is_query_context:
            normalized_vectors = [
                self._norm.normalize(vector) for vector in weighted_vectors
            ]
            return normalized_vectors
        return weighted_vectors

    def re_weight_vector(self, vector: Vector, context: ExecutionContext) -> Vector:
        parts = self._split_vector(vector)
        vector_and_nodes = list(zip(parts, self.parents))
        weighted_vector = self._apply_weights_and_concatenate(vector_and_nodes, context)
        normalized_vector = self._norm.normalize(weighted_vector)
        return normalized_vector

    def _apply_weights_and_concatenate(
        self,
        vector_and_nodes: list[tuple[Vector, OnlineNode]],
        context: ExecutionContext,
    ) -> Vector:
        weighted_vectors = (
            WeightArithmetics.apply_vector_weight(vector, parent.node_id, context)
            for vector, parent in vector_and_nodes
        )
        vector = reduce(lambda a, b: a.concatenate(b), weighted_vectors)
        return vector

    def _check_evaluation_inputs(
        self,
        parent_results: list[dict[OnlineNode, SingleEvaluationResult]],
    ) -> None:
        if any(
            result
            for parent_result in parent_results
            for result in parent_result.values()
            if not isinstance(result.value, Vector)
        ):
            raise ValidationException(
                f"{self.class_name} can only process `Vector` inputs."
            )

    def _split_vector(self, vector: Vector) -> list[Vector]:
        parents_without_duplicates = list(dict.fromkeys(self.parents))
        lengths = [
            cast(HasLength, parent).length for parent in parents_without_duplicates
        ]
        vectors: list[Vector] = vector.split(lengths)
        return vectors
