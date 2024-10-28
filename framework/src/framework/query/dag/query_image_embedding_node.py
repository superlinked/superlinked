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

from beartype.typing import Mapping, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.query.dag.exception import QueryEvaluationException
from superlinked.framework.query.dag.query_embedding_node import QueryEmbeddingNode
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryImageEmbeddingNode(QueryEmbeddingNode[Vector, ImageData]):
    def __init__(self, node: ImageEmbeddingNode, parents: Sequence[QueryNode]) -> None:
        super().__init__(node, parents, ImageData)
        self._validate_self()

    def _validate_self(self) -> None:
        if len(self.parents) > 1:
            raise QueryEvaluationException(
                f"{type(self).__name__} cannot have more than 1 parent."
            )

    @override
    def _evaluate_parents(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> list[QueryEvaluationResult]:
        if not self.parents:
            return []
        return [self.parents[0].evaluate_with_validation(inputs, context)]
