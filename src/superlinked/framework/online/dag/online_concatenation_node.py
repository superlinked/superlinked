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

from typing import cast

from superlinked.framework.common.dag.concatenation_node import ConcatenationNode
from superlinked.framework.common.dag.context import (
    SPACE_WEIGHT_PARAM_NAME,
    ExecutionContext,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.exception import ParentCountException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineConcatenationNode(DefaultOnlineNode[ConcatenationNode, Vector], HasLength):
    def __init__(
        self,
        node: ConcatenationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, parents, evaluation_result_store_manager)

    @classmethod
    def from_node(
        cls,
        node: ConcatenationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineConcatenationNode:
        if len(parents) == 0:
            raise ParentCountException(f"{cls.__name__} must have at least 1 parent.")
        return cls(node, parents, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[ConcatenationNode]:
        return ConcatenationNode

    @property
    def length(self) -> int:
        return self.node.length

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> Vector:
        self.__check_evaluation_inputs(parent_results)
        vector = sum(
            [
                self.__apply_vector_weight(result.value, parent.node_id, context)
                for parent, result in parent_results.items()
            ],
            Vector([]),
        )
        return vector.normalize()

    def re_weight_vector(
        self,
        vector: Vector,
        context: ExecutionContext,
    ) -> Vector:
        if len(self.parents) == 0:
            raise ParentCountException(
                f"{self.class_name} must have at least 1 parent."
            )
        parts = self._split_vector(vector)
        vector = sum(
            [
                self.__apply_vector_weight(part, parent.node_id, context)
                for part, parent in zip(parts, self.parents)
            ],
            Vector([]),
        )
        return vector.normalize()

    def __check_evaluation_inputs(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
    ) -> None:
        if len(parent_results.items()) == 0:
            raise ParentCountException(
                f"{self.class_name} must have at least 1 parent."
            )
        invalid_results = [
            result
            for _, result in parent_results.items()
            if not isinstance(result.value, Vector)
        ]
        if len(invalid_results) != 0:
            raise ValidationException(
                f"{self.class_name} can only process `Vector` inputs."
            )

    def __apply_vector_weight(
        self, vector: Vector, node_id: str, context: ExecutionContext
    ) -> Vector:
        weight = self.__get_weight_of_node(node_id, context)
        return vector * weight

    def __get_weight_of_node(self, node_id: str, context: ExecutionContext) -> float:
        weight_param = context.get_node_context_value(
            node_id, SPACE_WEIGHT_PARAM_NAME, float
        )
        return float(
            weight_param if weight_param is not None else self.node.default_weight
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
