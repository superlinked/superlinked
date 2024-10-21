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


class CustomEmbedding(Embedding[Vector, CustomEmbeddingConfig]):
    def __init__(self, embedding_config: CustomEmbeddingConfig) -> None:
        super().__init__(embedding_config)

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @override
    def embed(self, input_: Vector, context: ExecutionContext) -> Vector:
        return input_
