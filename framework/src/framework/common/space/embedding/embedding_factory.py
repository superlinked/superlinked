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

from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
    EmbeddingInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_type import (
    EmbeddingType,
)
from superlinked.framework.common.space.embedding.categorical_similarity_embedding import (
    CategoricalSimilarityEmbedding,
)
from superlinked.framework.common.space.embedding.custom_embedding import (
    CustomEmbedding,
)
from superlinked.framework.common.space.embedding.embedding import Embedding
from superlinked.framework.common.space.embedding.number_embedding import (
    NumberEmbedding,
)
from superlinked.framework.common.space.embedding.recency_embedding import (
    RecencyEmbedding,
)
from superlinked.framework.common.space.embedding.sentence_transformer_embedding import (
    SentenceTransformerEmbedding,
)

EMBEDDING_BY_EMBEDDING_TYPE: Mapping[EmbeddingType, type[Embedding]] = {
    EmbeddingType.CATEGORICAL: CategoricalSimilarityEmbedding,
    EmbeddingType.CUSTOM: CustomEmbedding,
    EmbeddingType.NUMBER: NumberEmbedding,
    EmbeddingType.RECENCY: RecencyEmbedding,
    EmbeddingType.TEXT: SentenceTransformerEmbedding,
}


class EmbeddingFactory:
    @staticmethod
    def create_embedding(
        embedding_config: EmbeddingConfig[EmbeddingInputT],
    ) -> Embedding[EmbeddingInputT, Any]:
        if embedding_class := EMBEDDING_BY_EMBEDDING_TYPE.get(
            embedding_config.embedding_type
        ):
            return embedding_class(embedding_config)
        raise ValueError(f"Unknown embedding mode: {embedding_config.embedding_type}")
