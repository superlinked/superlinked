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

import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.space.aggregation.aggregation import VectorAggregation
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    VectorAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.image_embedding_config import (
    ImageEmbeddingConfig,
    ModelHandler,
)
from superlinked.framework.common.space.embedding.embedding import Embedding
from superlinked.framework.common.space.embedding.model_manager import ModelManager
from superlinked.framework.common.space.embedding.open_clip_manager import (
    OpenClipManager,
)
from superlinked.framework.common.space.embedding.sentence_transformer_manager import (
    SentenceTransformerManager,
)

logger = structlog.getLogger()


class ImageEmbedding(Embedding[ImageData, ImageEmbeddingConfig]):
    def __init__(self, embedding_config: ImageEmbeddingConfig) -> None:
        super().__init__(embedding_config)
        self.manager = self.get_manager_type(self._config.model_handler)(
            self._config.model_name
        )

    @override
    def embed_multiple(
        self, inputs: Sequence[ImageData], context: ExecutionContext
    ) -> list[Vector]:
        images, descriptions = zip(
            *((input_.image, input_.description) for input_ in inputs)
        )
        embeddings = self.manager.embed(images + descriptions)
        if all(embedding is None for embedding in embeddings):
            return [Vector([0] * self._config.length)] * len(inputs)
        aggregation = VectorAggregation(VectorAggregationConfig(Vector))
        combined_embeddings = [
            aggregation.aggregate_weighted(
                [
                    Weighted(embedding)
                    for embedding in (image_embedding, description_embedding)
                    if embedding
                ],
                context,
            )
            for image_embedding, description_embedding in zip(
                embeddings[: len(inputs)], embeddings[len(inputs) :]
            )
        ]
        return combined_embeddings

    @override
    def embed(self, input_: ImageData, context: ExecutionContext) -> Vector:
        return self.embed_multiple([input_], context)[0]

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @classmethod
    def get_manager_type(cls, model_handler: ModelHandler) -> type[ModelManager]:
        manager_by_handler = {
            ModelHandler.SENTENCE_TRANSFORMERS: SentenceTransformerManager,
            ModelHandler.OPEN_CLIP: OpenClipManager,
        }
        try:
            return manager_by_handler[model_handler]
        except KeyError as e:
            raise ValueError(f"Unsupported model handler: {model_handler}") from e
