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

from beartype.typing import Generic, Iterable, Mapping, Sequence

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NT
from superlinked.framework.common.data_types import Vector
from superlinked.framework.query.dag.exception import QueryEvaluationException
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
    QueryEvaluationResultT,
)
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryNode(ABC, Generic[NT, QueryEvaluationResultT]):
    def __init__(self, node: NT, parents: Sequence[QueryNode]) -> None:
        super().__init__()
        self._node = node
        self.parents = parents

    @property
    def node(self) -> NT:
        return self._node

    @property
    def node_id(self) -> str:
        return self.node.node_id

    def evaluate_with_validation(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[QueryEvaluationResultT]:
        with context.dag_output_recorder.record_evaluation_exception(self.node_id):
            self._validate_evaluation_inputs(inputs)
            result = self._evaluate(inputs, context)
        context.dag_output_recorder.record(self.node_id, list(result) if isinstance(result, Iterable) else [result])
        return result

    def get_vector_parts(
        self, vectors: Sequence[Vector], node_ids: Sequence[str], context: ExecutionContext
    ) -> list[list[Vector]] | None:
        self._validate_get_vector_parts_inputs(vectors)
        return self._get_vector_parts(vectors, node_ids, context)

    def _validate_evaluation_inputs(self, inputs: Mapping[str, Sequence[QueryNodeInput]]) -> None:
        pass

    @abstractmethod
    def _evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[QueryEvaluationResultT]: ...

    def _validate_get_vector_parts_inputs(self, vectors: Sequence[Vector]) -> None:
        pass

    def _get_vector_parts(
        self,
        vectors: Sequence[Vector],  # pylint: disable=unused-argument
        node_ids: Sequence[str],  # pylint: disable=unused-argument
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> list[list[Vector]] | None:
        return None

    def _merge_inputs(
        self,
        inputs: Sequence[Mapping[str, Sequence[QueryNodeInput]]],
    ) -> dict[str, Sequence[QueryNodeInput]]:
        if not inputs:
            return {}
        merged_inputs_dict = dict(inputs[0])
        for inputs_item in inputs[1:]:
            for node_id, input_ in inputs_item.items():
                node_inputs = list(merged_inputs_dict.get(node_id, [])) + list(input_)
                merged_inputs_dict.update({node_id: node_inputs})
        return merged_inputs_dict

    def _validate_vectors_dimension(self, dimension: int, vectors: Sequence[Vector]) -> None:
        if wrong_dimensions := [vector.dimension for vector in vectors if vector.dimension != dimension]:
            raise QueryEvaluationException(
                f"{type(self).__name__} can only process vectors with {dimension} dimension,"
                f" got {wrong_dimensions}."
            )
