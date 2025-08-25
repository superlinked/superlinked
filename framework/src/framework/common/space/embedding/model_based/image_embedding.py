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
)
from superlinked.framework.common.space.embedding.model_based.model_embedding import (
    ModelEmbedding,
)


class ImageEmbedding(ModelEmbedding[ImageData, ImageEmbeddingConfig]):
    @override
    async def embed_multiple(self, inputs: Sequence[ImageData], context: ExecutionContext) -> list[Vector]:
        images = [input_.image for input_ in inputs]
        descriptions = [input_.description for input_ in inputs]
        valid_inputs = [inp for inp in (images + descriptions) if inp is not None]
        if not valid_inputs:
            return [self._config.default_vector] * len(inputs)
        valid_embeddings = await self._embedding_engine_manager.embed(
            self._config.model_handler,
            self._config.model_name,
            valid_inputs,
            context.is_query_context,
            self._config.model_cache_dir,
            self._config.embedding_engine_config,
        )
        embeddings = []
        valid_input_index = 0
        for input_ in images + descriptions:
            if input_ is not None:
                embeddings.append(valid_embeddings[valid_input_index])
                valid_input_index += 1
            else:
                embeddings.append(self._config.default_vector)
        aggregation = VectorAggregation(VectorAggregationConfig(Vector))
        combined_embeddings = [
            aggregation.aggregate_weighted(
                [Weighted(embedding) for embedding in (image_embedding, description_embedding) if embedding],
                context,
            )
            for image_embedding, description_embedding in zip(embeddings[: len(inputs)], embeddings[len(inputs) :])
        ]
        return combined_embeddings
