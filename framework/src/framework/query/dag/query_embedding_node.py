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

from beartype.typing import Generic, Mapping, Sequence, TypeVar, cast
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.embedding_node import EmbeddingNodeT
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

T = TypeVar("T")


class QueryEmbeddingNode(
    Generic[AggregationInputT, EmbeddingNodeT, NodeDataT],
    QueryNode[EmbeddingNodeT, Vector],
    ABC,
):
    def __init__(
        self,
        node: EmbeddingNodeT,
        parents: Sequence[QueryNode],
        input_type: type,
    ) -> None:
        super().__init__(node, parents)
        self._input_type = input_type
        self._multi_embedding_transformation = (
            TransformationFactory.create_multi_embedding_transformation(
                self.node.transformation_config
            )
        )
        self._aggregation_transformation = (
            TransformationFactory.create_aggregation_transformation(
                self.node.transformation_config
            )
        )

    @override
    def evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[Vector]:
        weighted_node_inputs, weighted_node_input_vectors = (
            self._validate_and_cast_node_inputs(inputs)
        )
        weighted_parent_results = self._validate_and_cast_parent_results(
            self._evaluate_parents(inputs, context)
        )
        weighted_embeddings = (
            self._embed_inputs(weighted_node_inputs, weighted_parent_results, context)
            + weighted_node_input_vectors
        )
        if weighted_embeddings:
            return QueryEvaluationResult(
                self._aggregation_transformation.transform(
                    cast(Sequence[Weighted], weighted_embeddings), context
                )
            )
        return QueryEvaluationResult(
            self.node.transformation_config.embedding_config.default_vector
        )

    @abstractmethod
    def _evaluate_parents(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> list[QueryEvaluationResult]:
        pass

    def _pre_process_node_inputs(
        self, inputs: Mapping[str, Sequence[QueryNodeInput]]
    ) -> Sequence[QueryNodeInput]:
        return inputs.get(self.node_id) or []

    def _validate_and_cast_node_inputs(
        self, inputs: Mapping[str, Sequence[QueryNodeInput]]
    ) -> tuple[list[Weighted], list[Weighted[Vector]]]:
        pre_processed_node_inputs = self._pre_process_node_inputs(inputs)
        simple_inputs = [
            input_ for input_ in pre_processed_node_inputs if not input_.to_invert
        ]
        weighted_input_items = [node_input.value for node_input in simple_inputs]
        inputs_to_be_inverted = [
            input_.value for input_ in pre_processed_node_inputs if input_.to_invert
        ]
        return self._validate_and_cast_items(
            weighted_input_items, self._input_type
        ), self._validate_and_cast_items(inputs_to_be_inverted, Vector)

    def _validate_and_cast_parent_results(
        self, parent_results: Sequence[QueryEvaluationResult]
    ) -> list[Weighted]:
        single_items = QueryEmbeddingNode._flat_parent_result_values(parent_results)
        weighted_single_items = [
            (
                single_item
                if isinstance(single_item, Weighted)
                else Weighted(single_item)
            )
            for single_item in single_items
        ]
        return self._validate_and_cast_items(weighted_single_items, self._input_type)

    def _validate_and_cast_items(
        self,
        weighted_items: Sequence[Weighted],
        input_type: type[T],
    ) -> list[Weighted[T]]:
        if wrong_types := [
            type(weighted_item.item).__name__
            for weighted_item in weighted_items
            if not isinstance(weighted_item.item, input_type)
        ]:
            raise QueryEvaluationException(
                f"{type(self).__name__} can only evaluate {input_type.__name__}, "
                + f"got {wrong_types}."
            )
        return cast(list[Weighted[T]], weighted_items)

    def _embed_inputs(
        self,
        weighted_node_inputs: Sequence[Weighted],
        weighted_parent_results: Sequence[Weighted],
        context: ExecutionContext,
    ) -> list[Weighted[Vector]]:
        if weighted_node_inputs or weighted_parent_results:
            weighted_items = list(weighted_node_inputs) + list(weighted_parent_results)
            embedding_inputs = [weighted_item.item for weighted_item in weighted_items]
            embeddings = self._multi_embedding_transformation.transform(
                embedding_inputs, context
            )
            return [
                Weighted(embedding, weighted_item.weight)
                for weighted_item, embedding in zip(weighted_items, embeddings)
            ]
        return []

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
