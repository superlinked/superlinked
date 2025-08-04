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


from beartype.typing import Any, Mapping

from superlinked.framework.common.exception import NotImplementedException
from superlinked.framework.common.space.config.embedding.categorical_similarity_embedding_config import (
    CategoricalSimilarityEmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.custom_embedding_config import (
    CustomEmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
    EmbeddingInputT,
)
from superlinked.framework.common.space.config.embedding.image_embedding_config import (
    ImageEmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.number_embedding_config import (
    NumberEmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.recency_embedding_config import (
    RecencyEmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.text_similarity_embedding_config import (
    TextSimilarityEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.categorical_similarity_embedding import (
    CategoricalSimilarityEmbedding,
)
from superlinked.framework.common.space.embedding.custom_embedding import (
    CustomEmbedding,
)
from superlinked.framework.common.space.embedding.embedding import Embedding
from superlinked.framework.common.space.embedding.model_based.embedding_engine_manager import (
    EmbeddingEngineManager,
)
from superlinked.framework.common.space.embedding.model_based.image_embedding import (
    ImageEmbedding,
)
from superlinked.framework.common.space.embedding.model_based.text_embedding import (
    TextEmbedding,
)
from superlinked.framework.common.space.embedding.number_embedding import (
    NumberEmbedding,
)
from superlinked.framework.common.space.embedding.recency_embedding import (
    RecencyEmbedding,
)

EMBEDDING_BY_CONFIG_CLASS: Mapping[type[EmbeddingConfig], type[Embedding]] = {
    CategoricalSimilarityEmbeddingConfig: CategoricalSimilarityEmbedding,
    CustomEmbeddingConfig: CustomEmbedding,
    NumberEmbeddingConfig: NumberEmbedding,
    RecencyEmbeddingConfig: RecencyEmbedding,
    TextSimilarityEmbeddingConfig: TextEmbedding,
    ImageEmbeddingConfig: ImageEmbedding,
}


class EmbeddingFactory:
    @staticmethod
    def create_embedding(
        embedding_config: EmbeddingConfig[EmbeddingInputT], embedding_engine_manager: EmbeddingEngineManager
    ) -> Embedding[EmbeddingInputT, Any]:
        if embedding_class := EMBEDDING_BY_CONFIG_CLASS.get(type(embedding_config)):
            return embedding_class(embedding_config, embedding_engine_manager)
        raise NotImplementedException(
            "Unsupported embedding config type.", embedding_config_type=type(embedding_config).__name__
        )
