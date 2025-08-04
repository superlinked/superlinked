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

from beartype.typing import Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.number_embedding_node import NumberEmbeddingNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.space.config.embedding.number_embedding_config import (
    Mode,
    NumberEmbeddingConfig,
)
from superlinked.framework.common.space.normalization.normalization_factory import (
    NormalizationFactory,
)
from superlinked.framework.query.dag.query_embedding_orphan_node import (
    QueryEmbeddingOrphanNode,
)
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import (
    QueryNodeInput,
    QueryNodeInputValue,
)


class QueryNumberEmbeddingNode(QueryEmbeddingOrphanNode[float, NumberEmbeddingNode, float]):
    def __init__(self, node: NumberEmbeddingNode, parents: Sequence[QueryNode]) -> None:
        super().__init__(node, parents, float)
        self._normalization = NormalizationFactory.create_normalization(
            self.node.transformation_config.normalization_config
        )
        self._embedding_config = cast(NumberEmbeddingConfig, self.node.transformation_config.embedding_config)

    @override
    def _pre_process_node_input(self, node_input: QueryNodeInput) -> QueryNodeInput:
        if isinstance(node_input.value.item, Vector):
            return node_input
        if isinstance(node_input.value.item, float):
            return node_input
        return QueryNodeInput(
            QueryNodeInputValue(float(node_input.value.item), node_input.value.weight),
            node_input.to_invert,
        )

    @override
    async def _evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[Vector]:
        if self._embedding_config.mode not in (Mode.MINIMUM, Mode.MAXIMUM):
            return await super()._evaluate(inputs, context)
        if self._min_or_max_weight_is_zero(inputs):
            return QueryEvaluationResult(Vector.init_zero_vector(self.node.length))
        return QueryEvaluationResult(self._embedding_config.default_vector)

    def _min_or_max_weight_is_zero(self, inputs: Mapping[str, Sequence[QueryNodeInput]]) -> None | float | int:
        corresponding_inputs = inputs.get(self.node_id)
        if not corresponding_inputs:
            return None
        if len(corresponding_inputs) > 1:
            raise InvalidStateException(
                f"Number embedding node with mode {self._embedding_config.mode.name} supports only a single input.",
                input_count=len(corresponding_inputs),
            )
        input_value = corresponding_inputs[0].value
        if not isinstance(input_value.item, Vector):
            raise InvalidStateException(
                f"Number embedding node with mode {self._embedding_config.mode.name} can only handle a Vector input.",
                input_count=len(corresponding_inputs),
            )
        weight = input_value.weight.get(self.node_id) if isinstance(input_value.weight, dict) else input_value.weight
        return weight == 0
