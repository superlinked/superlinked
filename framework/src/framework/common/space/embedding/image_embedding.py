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

from pathlib import Path

import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.aggregation.aggregation import VectorAggregation
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    VectorAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.image_embedding_config import (
    ImageEmbeddingConfig,
    ModelHandler,
)
from superlinked.framework.common.space.embedding.embedding import Embedding
from superlinked.framework.common.space.embedding.modal_manager import ModalManager
from superlinked.framework.common.space.embedding.model_manager import (
    ModelEmbeddingInputT,
)
from superlinked.framework.common.space.embedding.open_clip_manager import (
    OpenClipManager,
)
from superlinked.framework.common.space.embedding.sentence_transformer_manager import (
    SentenceTransformerManager,
)
from superlinked.framework.common.util.image_util import ImageUtil

logger = structlog.getLogger()

ManagerT = SentenceTransformerManager | OpenClipManager | ModalManager

MANAGER_BY_HANDLER: dict[ModelHandler, type[ManagerT]] = {
    ModelHandler.SENTENCE_TRANSFORMERS: SentenceTransformerManager,
    ModelHandler.OPEN_CLIP: OpenClipManager,
    ModelHandler.MODAL: ModalManager,
}


class ImageEmbedding(Embedding[ImageData, ImageEmbeddingConfig]):
    def __init__(
        self,
        embedding_config: ImageEmbeddingConfig,
    ) -> None:
        super().__init__(embedding_config)
        self.manager = ImageEmbedding.init_manager(
            self._config.model_handler, self._config.model_name, self._config.model_cache_dir
        )

    @override
    def embed_multiple(self, inputs: Sequence[ImageData], context: ExecutionContext) -> list[Vector]:
        images_and_descriptions = self._prepare_images_and_descriptions(inputs)
        embeddings = self.manager.embed(images_and_descriptions, context)
        if all(embedding is None for embedding in embeddings):
            return [Vector.init_zero_vector(self._config.length)] * len(inputs)
        aggregation = VectorAggregation(VectorAggregationConfig(Vector))
        combined_embeddings = [
            aggregation.aggregate_weighted(
                [Weighted(embedding) for embedding in (image_embedding, description_embedding) if embedding],
                context,
            )
            for image_embedding, description_embedding in zip(embeddings[: len(inputs)], embeddings[len(inputs) :])
        ]
        return combined_embeddings

    @override
    def embed(self, input_: ImageData, context: ExecutionContext) -> Vector:
        return self.embed_multiple([input_], context)[0]

    @property
    @override
    def length(self) -> int:
        return self._config.length

    def _prepare_images_and_descriptions(self, inputs: Sequence[ImageData]) -> list[ModelEmbeddingInputT | None]:
        descriptions = [input_.description for input_ in inputs]
        images = [input_.image for input_ in inputs]
        if Settings().SUPERLINKED_RESIZE_IMAGES:
            images = [ImageUtil.resize_for_embedding(image) if image is not None else None for image in images]
        return [*images, *descriptions]

    @classmethod
    def init_manager(cls, model_handler: ModelHandler, model_name: str, model_cache_dir: Path | None) -> ManagerT:
        if manager_type := MANAGER_BY_HANDLER.get(model_handler):
            return manager_type(model_name, model_cache_dir)
        raise ValueError(f"Unsupported model handler: {model_handler}")
