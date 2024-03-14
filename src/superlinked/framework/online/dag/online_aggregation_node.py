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
from typing import cast

from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    MismatchingDimensionException,
    ValidationException,
)
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.exception import ParentCountException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineAggregationNode(DefaultOnlineNode[AggregationNode, Vector], HasLength):
    def __init__(
        self,
        node: AggregationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, parents, evaluation_result_store_manager)
        OnlineAggregationNode.__validate_parents(parents)

    @classmethod
    def from_node(
        cls,
        node: AggregationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineAggregationNode:
        return cls(node, parents, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[AggregationNode]:
        return AggregationNode

    @property
    def length(self) -> int:
        return self.node.length

    @classmethod
    def __validate_parents(cls, parents: list[OnlineNode]) -> None:
        if len(parents) == 0:
            raise ParentCountException(f"{cls.__name__} must have at least 1 parent.")
        length = cast(HasLength, parents[0]).length
        if any(
            parent for parent in parents if cast(HasLength, parent).length != length
        ):
            raise ValidationException(
                f"{cls.__name__} must have parents with the same length."
            )

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> Vector:
        self._check_evaluation_inputs(parent_results)
        weighted_vectors = self._get_weighted_vectors(parent_results)
        aggregation = reduce(lambda a, b: a.aggregate(b), weighted_vectors)
        return aggregation.normalize()

    def _check_evaluation_inputs(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
    ) -> None:
        invalid_type_result_types = [
            result.__class__.__name__
            for _, result in parent_results.items()
            if not isinstance(result.value, Vector)
        ]
        if any(invalid_type_result_types):
            raise ValidationException(
                f"{self.class_name} can only process `Vector` inputs"
                + f", got {invalid_type_result_types}"
            )
        filtered_parent_results: dict[OnlineNode, SingleEvaluationResult[Vector]] = {
            parent: result
            for parent, result in parent_results.items()
            if not cast(Vector, result.value).is_empty
        }
        if not any(filtered_parent_results.items()):
            raise ParentCountException(
                f"{self.class_name} must have at least 1 parent with valid input."
            )
        invalid_length_results = [
            result
            for _, result in filtered_parent_results.items()
            if result.value.dimension != self.length
        ]
        if any(invalid_length_results):
            raise MismatchingDimensionException(
                f"{self.class_name} can only process inputs having same length"
                + f", got {invalid_length_results[0].value.dimension}"
            )

    def _get_weighted_vectors(
        self, parent_results: dict[OnlineNode, SingleEvaluationResult]
    ) -> list[Vector]:
        node_id_weight_map = {
            weighted_parent.item.node_id: weighted_parent.weight
            for weighted_parent in self.node.weighted_parents
        }
        return [
            result.value * node_id_weight_map[cast(Node, parent.node).node_id]
            for parent, result in cast(
                dict[OnlineNode, SingleEvaluationResult[Vector]], parent_results
            ).items()
            if not cast(Vector, result.value).is_empty
        ]
