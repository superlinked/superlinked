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


from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.custom_embedding_config import (
    CustomEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.embedding import Embedding
from superlinked.framework.common.space.embedding.model_based.embedding_engine_manager import (
    EmbeddingEngineManager,
)


class CustomEmbedding(Embedding[Vector, CustomEmbeddingConfig]):
    def __init__(
        self, embedding_config: CustomEmbeddingConfig, embedding_engine_manager: EmbeddingEngineManager
    ) -> None:
        super().__init__(embedding_config, embedding_engine_manager)

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @override
    async def embed(self, input_: Vector, context: ExecutionContext) -> Vector:
        return input_
