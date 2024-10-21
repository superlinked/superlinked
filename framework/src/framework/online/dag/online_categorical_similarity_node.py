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

from beartype.typing import cast
from typing_extensions import override

from superlinked.framework.common.dag.categorical_similarity_node import (
    CategoricalSimilarityNode,
)
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.transform.transform import Step
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType


class OnlineCategoricalSimilarityNode(
    OnlineNode[CategoricalSimilarityNode, Vector], HasLength
):
    def __init__(
        self,
        node: CategoricalSimilarityNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(
            node,
            parents,
            storage_manager,
            ParentValidationType.LESS_THAN_TWO_PARENTS,
        )
        self._embedding_transformation = (
            TransformationFactory.create_embedding_transformation(
                self.node.transformation_config
            )
        )

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @property
    def embedding_transformation(self) -> Step[list[str], Vector]:
        return self._embedding_transformation

    @override
    def evaluate_self(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[Vector]]:
        return [self.evaluate_self_single(schema, context) for schema in parsed_schemas]

    def evaluate_self_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[Vector]:
        if self.node.transformation_config.embedding_config.should_return_default(
            context
        ):
            result = self.node.transformation_config.embedding_config.default_vector
        elif len(self.parents) == 0:
            result = self.load_stored_result_or_raise_exception(parsed_schema)
        else:
            input_: str | list[str] = (
                cast(
                    OnlineNode[Node[str | list[str]], str | list[str]], self.parents[0]
                )
                .evaluate_next_single(parsed_schema, context)
                .main.value
            )
            categories = input_ if isinstance(input_, list) else [input_]
            result = self.embedding_transformation.transform(categories, context)
        return EvaluationResult(self._get_single_evaluation_result(result))
