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

from beartype.typing import Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    MismatchingDimensionException,
    ValidationException,
)
from superlinked.framework.common.interface.has_embedding import HasEmbedding
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType


class OnlineAggregationNode(DefaultOnlineNode[AggregationNode, Vector], HasLength):
    def __init__(
        self,
        node: AggregationNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(
            node,
            parents,
            storage_manager,
            ParentValidationType.AT_LEAST_ONE_PARENT,
        )
        OnlineAggregationNode._validate_parents(parents)
        self._node_id_weight_map: dict[str, float] = {
            weighted_parent.item.node_id: weighted_parent.weight
            for weighted_parent in self.node.weighted_parents
        }

    @property
    def length(self) -> int:
        return self.node.length

    @classmethod
    def _validate_parents(cls, parents: list[OnlineNode]) -> None:
        length = cast(HasLength, parents[0]).length
        if any(
            parent for parent in parents if cast(HasLength, parent).length != length
        ):
            raise ValidationException(
                f"{cls.__name__} must have parents with the same length."
            )

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
    ) -> Vector:
        self._check_evaluation_inputs(parent_results)
        weighted_vector_by_parent = self._get_weighted_vector_by_parent(parent_results)

        if self._no_event_present(weighted_vector_by_parent):
            return list(weighted_vector_by_parent.values())[0].item

        online_nodes = list(weighted_vector_by_parent.keys())
        self._validate_embeddings(online_nodes)

        embedding = HasEmbedding.get_common_embedding(
            cast(list[HasEmbedding], online_nodes)
        )

        return self.node.aggregation.aggregate_weighted(
            list(weighted_vector_by_parent.values()), embedding, context
        )

    def _validate_embeddings(self, online_nodes: Sequence[OnlineNode]) -> None:
        if not all(
            isinstance(online_node, HasEmbedding) for online_node in online_nodes
        ):
            raise ValidationException(
                f"Parents of {self.class_name} must have embedding."
            )

    def _no_event_present(
        self, weighted_vectors: dict[OnlineNode, Weighted[Vector]]
    ) -> bool:
        return len(weighted_vectors) == 1

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

    def _get_weighted_vector_by_parent(
        self, parent_results: dict[OnlineNode, SingleEvaluationResult]
    ) -> dict[OnlineNode, Weighted[Vector]]:
        return {
            parent: Weighted(
                result.value, self._node_id_weight_map[parent.node.node_id]
            )
            for parent, result in parent_results.items()
            if result.value and not result.value.is_empty
        }
