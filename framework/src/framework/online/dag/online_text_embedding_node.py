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
from superlinked.framework.common.dag.text_embedding_node import TextEmbeddingNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.space.embedding.model_based.singleton_embedding_engine_manager import (
    SingletonEmbeddingEngineManager,
)
from superlinked.framework.common.transform.transform import Step
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.online_entity_cache import OnlineEntityCache


class OnlineTextEmbeddingNode(DefaultOnlineNode[TextEmbeddingNode, Vector], HasLength):
    def __init__(
        self,
        node: TextEmbeddingNode,
        parents: list[OnlineNode],
    ) -> None:
        super().__init__(node, parents)
        self._embedding_transformation = self._init_embedding_transformation()

    def _init_embedding_transformation(self) -> Step[Sequence[str], list[Vector]]:
        return TransformationFactory.create_multi_embedding_transformation(
            self.node.transformation_config, SingletonEmbeddingEngineManager()
        )

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @property
    def embedding_transformation(self) -> Step[Sequence[str], list[Vector]]:
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
        parent_results: Sequence[dict[OnlineNode, SingleEvaluationResult[str]]],
        context: ExecutionContext,
    ) -> Sequence[Vector | None]:
        none_indices = [i for i, parent_result in enumerate(parent_results) if not parent_result]
        non_none_parent_results = [parent_result for parent_result in parent_results if parent_result]
        input_ = list(
            map(
                lambda parent_result: list(parent_result.values())[0].value,
                non_none_parent_results,
            )
        )
        embedded_texts: list[Vector | None] = list(await self.__embed_texts(input_, context))
        for i in none_indices:
            embedded_texts.insert(i, None)
        return embedded_texts

    async def __embed_texts(self, texts: Sequence[str], context: ExecutionContext) -> list[Vector]:
        return await self.embedding_transformation.transform(texts, context)
