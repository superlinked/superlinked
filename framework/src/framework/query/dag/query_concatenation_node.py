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
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import NodeDataTypes, Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.normalization.normalization import (
    ConstantNorm,
    L2Norm,
)
from superlinked.framework.query.dag.exception import QueryEvaluationException
from superlinked.framework.query.dag.invert_if_addressed_query_node import (
    InvertIfAddressedQueryNode,
)
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryConcatenationNode(InvertIfAddressedQueryNode[ConcatenationNode, Vector]):
    def __init__(
        self,
        node: ConcatenationNode,
        parents: Sequence[QueryNode[Node[Vector], Vector]],
    ) -> None:
        super().__init__(node, parents)
        self._denormalizer = self._create_denormalizer()

    def _create_denormalizer(self) -> ConstantNorm:
        return ConstantNorm(
            self.node.create_normalization_config([1.0] * len(self.node.parents))
        )

    @override
    def invert_and_readdress(
        self, node_inputs: Sequence[Weighted[NodeDataTypes]]
    ) -> dict[str, list[QueryNodeInput]]:
        # All of the inputs are vectors having the same dimension as the CN.
        self._validate_iputs_to_be_inverted(node_inputs)
        # Each vector (outer list item) has the same number of
        # parts (inner list items) as the number of parents.
        split_weighted_vectors: list[list[Weighted[Vector]]] = [
            self._split_weighted_vector(cast(Weighted[Vector], node_input))
            for node_input in node_inputs
        ]
        return self._address_split_weighted_vectors(split_weighted_vectors)

    def _validate_iputs_to_be_inverted(
        self, node_inputs: Sequence[Weighted[NodeDataTypes]]
    ) -> None:
        if any(
            invalid_inputs := [
                node_input
                for node_input in node_inputs
                if not isinstance(node_input.item, Vector)
            ]
        ):
            raise QueryEvaluationException(
                "The inputs that need to be inverted must be "
                + f"vectors, got {invalid_inputs}"
            )
        if any(
            invalid_inputs_lengths := [
                cast(Vector, node_input.item).dimension
                for node_input in node_inputs
                if cast(Vector, node_input.item).dimension != self.node.length
            ]
        ):
            raise QueryEvaluationException(
                "The inputs that need to be inverted must have the same dimension "
                + f"as the concatenation node, got {invalid_inputs_lengths}"
            )

    def _split_weighted_vector(
        self, weighted_vector: Weighted[Vector]
    ) -> list[Weighted[Vector]]:
        vector = weighted_vector.item
        parents_without_duplicates = list(dict.fromkeys(self.parents))
        lengths = [
            cast(HasLength, parent.node).length for parent in parents_without_duplicates
        ]
        vectors = vector.split(lengths)
        return [
            Weighted(self._denormalizer.denormalize(vector), weighted_vector.weight)
            for vector in vectors
        ]

    def _address_split_weighted_vectors(
        self, split_weighted_vectors: Sequence[Sequence[Weighted[Vector]]]
    ) -> dict[str, list[QueryNodeInput]]:
        return {
            parent.node_id: [
                QueryNodeInput(weighted_vectors[i], to_invert=True)
                for weighted_vectors in split_weighted_vectors
            ]
            for i, parent in enumerate(self.parents)
        }

    def _validate_parent_results(
        self, parent_results: Sequence[QueryEvaluationResult]
    ) -> None:
        super()._validate_parent_results(parent_results)
        if invalid_parent_result_types := {
            type(parent_result.value).__name__
            for parent_result in parent_results
            if not isinstance(parent_result.value, Vector)
        }:
            raise QueryEvaluationException(
                f"Parent results must be vectors, got {invalid_parent_result_types}"
            )

    @override
    def _evaluate_parent_results(
        self, parent_results: Sequence[QueryEvaluationResult], context: ExecutionContext
    ) -> QueryEvaluationResult[Vector]:
        vectors_with_weights = [
            (
                cast(Vector, result.value),
                context.get_weight_of_node(self.parents[i].node_id),
            )
            for i, result in enumerate(parent_results)
        ]
        weighted_vectors = [vector * weight for vector, weight in vectors_with_weights]
        norm = ConstantNorm(
            self.node.create_normalization_config(
                [weight for _, weight in vectors_with_weights]
            )
        )
        vector = norm.normalize(reduce(lambda a, b: a.concatenate(b), weighted_vectors))
        compensation_factor = self._calculate_compensation_factor(weighted_vectors)
        return QueryEvaluationResult(vector * compensation_factor)

    def _calculate_compensation_factor(
        self, weighted_vectors: Sequence[Vector]
    ) -> float:
        num_non_0_spaces = len(
            [
                weighted_vector
                for weighted_vector in weighted_vectors
                if L2Norm().norm(weighted_vector.value) != 0
            ]
        )
        if num_non_0_spaces == 0:
            return 1.0
        return len(self.parents) / num_non_0_spaces
