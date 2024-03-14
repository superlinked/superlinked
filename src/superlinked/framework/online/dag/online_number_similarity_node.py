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

from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.number_similarity_node import NumberSimilarityNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import DagEvaluationException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.exception import ParentCountException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineNumberSimilarityNode(OnlineNode[NumberSimilarityNode, Vector], HasLength):
    def __init__(
        self,
        node: NumberSimilarityNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, parents, evaluation_result_store_manager)

    @classmethod
    def from_node(
        cls,
        node: NumberSimilarityNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineNumberSimilarityNode:
        if len(parents) > 1:
            raise ParentCountException(
                f"{cls.__name__} cannot have more than one parents, got {len(parents)}."
            )
        return cls(node, parents, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[NumberSimilarityNode]:
        return NumberSimilarityNode

    @property
    def length(self) -> int:
        return self.node.length

    @override
    def evaluate_self(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[Vector]:
        if len(self.parents) > 1:
            raise ParentCountException(
                f"{self.__class__.__name__} cannot have more than one parents, got {len(self.parents)}."
            )

        if len(self.parents) == 0:
            stored_result = self.load_stored_result(
                parsed_schema.id_, parsed_schema.schema
            )
            if stored_result is None:
                raise DagEvaluationException(
                    f"{self.class_name} doesn't have a stored result."
                )
            return EvaluationResult(self._get_single_evaluation_result(stored_result))

        input_: EvaluationResult[float | int] = cast(
            OnlineNode[Node[float | int], float | int], self.parents[0]
        ).evaluate_next(parsed_schema, context)
        transformed_input_value = self.node.embedding.transform(
            input_.main.value, context.is_query_context()
        )
        main = self._get_single_evaluation_result(transformed_input_value)
        return EvaluationResult(main)
