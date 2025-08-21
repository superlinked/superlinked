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

from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.recency_node import RecencyNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.transform.transform import Step
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.online_entity_cache import OnlineEntityCache

DAY_IN_SECONDS: int = 24 * 60 * 60


class OnlineRecencyNode(DefaultOnlineNode[RecencyNode, Vector], HasLength):
    def __init__(
        self,
        node: RecencyNode,
        parents: list[OnlineNode],
    ) -> None:
        super().__init__(node, parents)
        self._embedding_transformation = TransformationFactory.create_embedding_transformation(
            self.node.transformation_config
        )

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @property
    def embedding_transformation(self) -> Step[int, Vector]:
        return self._embedding_transformation

    @override
    async def get_fallback_results(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        online_entity_cache: OnlineEntityCache,
    ) -> list[Vector]:
        schemas_with_object_ids = [(parsed_schema.schema, parsed_schema.id_) for parsed_schema in parsed_schemas]
        stored_results = await self.load_stored_results(schemas_with_object_ids, online_entity_cache)
        return [
            Vector.init_zero_vector(self.length) if stored_result is None else stored_result
            for stored_result in stored_results
        ]

    @override
    async def _evaluate_singles(
        self,
        parent_results: Sequence[dict[OnlineNode, SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> Sequence[Vector | None]:
        return [await self._evaluate_single(parent_result, context) for parent_result in parent_results]

    async def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> Vector | None:
        if len(parent_results.items()) != 1:
            return None
        input_: int = list(parent_results.values())[0].value
        return await self.embedding_transformation.transform(input_, context)
