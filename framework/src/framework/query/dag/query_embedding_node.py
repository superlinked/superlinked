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

from abc import ABC, abstractmethod

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
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
    QueryEvaluationResultT,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryEmbeddingNode(
    Generic[AggregationInputT, NodeDataT],
    QueryNode[EmbeddingNode[AggregationInputT, NodeDataT], Vector],
    ABC,
):
    def __init__(
        self,
        node: EmbeddingNode[AggregationInputT, NodeDataT],
        parents: Sequence[QueryNode],
        input_type: type[AggregationInputT | NodeDataT],
    ) -> None:
        super().__init__(node, parents)
        self._input_type = input_type
        self._aggregated_embedding_transformation = (
            TransformationFactory.create_aggregated_embedding_transformation(
                self.node.transformation_config,
            )
        )

    @override
    def evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[Vector]:
        weighted_node_input_items = self._validate_and_cast_node_inputs(
            inputs.get(self.node_id) or []
        )
        weighted_parent_result_items = self._validate_and_cast_parent_results(
            self._evaluate_parents(inputs, context)
        )
        if weighted_node_input_items or weighted_parent_result_items:
            all_items = weighted_node_input_items + weighted_parent_result_items
            return QueryEvaluationResult(
                self._aggregated_embedding_transformation.transform(
                    cast(Sequence[Weighted], all_items), context
                )
            )
        return QueryEvaluationResult(
            self.node.transformation_config.embedding_config.default_vector
        )

    def _pre_process_node_input(self, node_input: QueryNodeInput) -> QueryNodeInput:
        return node_input

    @abstractmethod
    def _evaluate_parents(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> list[QueryEvaluationResult]:
        pass

    def _validate_and_cast_node_inputs(
        self, node_inputs: Sequence[QueryNodeInput]
    ) -> list[Weighted[AggregationInputT]] | list[Weighted[NodeDataT]]:
        weighted_input_items = [
            self._pre_process_node_input(node_input).value for node_input in node_inputs
        ]
        return self._validate_and_cast_items(weighted_input_items)

    def _validate_and_cast_parent_results(
        self, parent_results: Sequence[QueryEvaluationResult]
    ) -> list[Weighted[AggregationInputT]] | list[Weighted[NodeDataT]]:
        single_items = QueryEmbeddingNode._flat_parent_result_values(parent_results)
        weighted_single_items = [
            (
                single_item
                if isinstance(single_item, Weighted)
                else Weighted(single_item)
            )
            for single_item in single_items
        ]
        return self._validate_and_cast_items(weighted_single_items)

    @staticmethod
    def _flat_parent_result_values(
        parent_results: Sequence[QueryEvaluationResult[QueryEvaluationResultT]],
    ) -> list[QueryEvaluationResultT | Weighted[QueryEvaluationResultT]]:
        single_items = list[QueryEvaluationResultT | Weighted[QueryEvaluationResultT]]()
        for parent_result in parent_results:
            if isinstance(parent_result.value, list):
                single_items.extend(parent_result.value)
            else:
                single_items.append(parent_result.value)
        return single_items

    def _validate_and_cast_items(
        self, weighted_items: Sequence[Weighted[NodeDataT]]
    ) -> list[Weighted[AggregationInputT]] | list[Weighted[NodeDataT]]:
        if wrong_types := [
            type(weighted_item.item).__name__
            for weighted_item in weighted_items
            if not isinstance(weighted_item.item, self._input_type)
        ]:
            raise QueryEvaluationException(
                f"{type(self).__name__} can only evaluate {self._input_type.__name__}, "
                + f"got {wrong_types}."
            )
        return cast(
            list[Weighted[AggregationInputT]] | list[Weighted[AggregationInputT]],
            weighted_items,
        )
