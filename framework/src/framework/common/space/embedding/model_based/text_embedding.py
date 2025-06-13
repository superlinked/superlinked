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
from superlinked.framework.common.space.config.embedding.text_similarity_embedding_config import (
    TextSimilarityEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.model_based.embedding_engine_manager import (
    EmbeddingEngineManager,
)
from superlinked.framework.common.space.embedding.model_based.model_embedding import (
    ModelEmbedding,
)
from superlinked.framework.common.space.embedding.model_based.text_embedding_cache import (
    TextEmbeddingCache,
)


class TextEmbedding(ModelEmbedding[str, TextSimilarityEmbeddingConfig]):
    def __init__(
        self, embedding_config: TextSimilarityEmbeddingConfig, embedding_engine_manager: EmbeddingEngineManager
    ) -> None:
        super().__init__(embedding_config, embedding_engine_manager)
        self._cache = TextEmbeddingCache(self._config.cache_size)

    @override
    async def embed_multiple(self, inputs: Sequence[str], context: ExecutionContext) -> list[Vector]:
        unique_inputs = list(dict.fromkeys(inputs))  # used instead of set() to keep original order
        inputs_to_embed, found_indices, existing_vectors = self._cache.calculate_cache_info(unique_inputs)
        new_vectors = await self._embedding_engine_manager.embed(
            self._config.model_handler,
            self._config.model_name,
            inputs_to_embed,
            context.is_query_context,
            self._config.model_cache_dir,
            self._config.embedding_engine_config,
        )
        self._cache.update(inputs_to_embed, new_vectors)
        combined_vectors = self._cache.combine_vectors(inputs_to_embed, found_indices, existing_vectors, new_vectors)
        input_to_vector = dict(zip(unique_inputs, combined_vectors))
        vectors_mapped_back_to_input_len = [input_to_vector[input_] for input_ in inputs]
        return vectors_mapped_back_to_input_len
