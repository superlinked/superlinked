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

from beartype.typing import Generic, Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.node import NodeDataT
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.query.dag.exception import QueryEvaluationException
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryEmbeddingNode(
    QueryNode[EmbeddingNode[AggregationInputT, NodeDataT], Vector],
    Generic[AggregationInputT, NodeDataT],
):

    def __init__(
        self,
        node: EmbeddingNode[AggregationInputT, NodeDataT],
        parents: Sequence[QueryNode],
        input_type: type[AggregationInputT | NodeDataT],
    ) -> None:
        super().__init__(node, parents)
        self._validate_self()
        self._input_type = input_type
        self._aggregated_embedding_transformation = (
            TransformationFactory.create_aggregated_embedding_transformation(
                self.node.transformation_config,
            )
        )

    def _validate_self(self) -> None:
        if self.parents:
            raise QueryEvaluationException(
                f"{type(self).__name__} cannot have parents."
            )

    @override
    def evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> Vector:
        if node_inputs := inputs.get(self.node_id):
            weighted_items = [node_input.value for node_input in node_inputs]
            if any(
                weighted_item
                for weighted_item in weighted_items
                if not isinstance(weighted_item.item, self._input_type)
            ):
                raise QueryEvaluationException(
                    f"{type(self).__name__} can only evaluate {self._input_type.__name__}."
                )
            return self._aggregated_embedding_transformation.transform(
                cast(Sequence[Weighted], weighted_items), context
            )
        return self.node.transformation_config.embedding_config.default_vector

    def pre_process_node_input(
        self, node_inputs: Sequence[QueryNodeInput]
    ) -> Sequence[QueryNodeInput]:
        return node_inputs
