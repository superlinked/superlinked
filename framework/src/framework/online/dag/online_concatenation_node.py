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
from superlinked.framework.common.space.normalization import L2Norm
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
            node,
            parents,
            storage_manager,
            ParentValidationType.AT_LEAST_ONE_PARENT,
        )

    @property
    def length(self) -> int:
        return self.node.length

    @override
    def _evaluate_singles(
        self,
        parent_results: list[dict[OnlineNode, SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> Sequence[Vector | None]:
        self.__check_evaluation_inputs(parent_results)
        vectors = [
            reduce(
                lambda a, b: a.concatenate(b),
                (
                    WeightArithmetics.apply_vector_weight(
                        result.value, parent.node_id, context
                    )
                    for parent, result in parent_result.items()
                ),
            )
            for parent_result in parent_results
        ]
        if context.is_query_context:
            return vectors
        l2_norm = L2Norm()
        return [l2_norm.normalize(vector) for vector in vectors]

    def re_weight_vector(
        self,
        vector: Vector,
        context: ExecutionContext,
    ) -> Vector:
        parts = self._split_vector(vector)
        vector = reduce(
            lambda a, b: a.concatenate(b),
            (
                WeightArithmetics.apply_vector_weight(part, parent.node_id, context)
                for part, parent in zip(parts, self.parents)
            ),
        )
        return L2Norm().normalize(vector)

    def __check_evaluation_inputs(
        self,
        parent_results: list[dict[OnlineNode, SingleEvaluationResult]],
    ) -> None:
        invalid_results = [
            result
            for parent_result in parent_results
            for result in parent_result.values()
            if not isinstance(result.value, Vector)
        ]
        if len(invalid_results) != 0:
            raise ValidationException(
                f"{self.class_name} can only process `Vector` inputs."
            )

    def _split_vector(self, vector: Vector) -> list[Vector]:
        if vector is None:
            vector = Vector([])
        offset: int = 0
        parts: list[Vector] = []
        vector_value = vector.value
        for parent in self.parents:
            parent_length = cast(HasLength, parent).length
            parts.append(Vector(vector_value[offset : offset + parent_length]))
            offset += parent_length
        return parts
