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

from dataclasses import dataclass

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.space.config.embedding.model_based_embedding_config import (
    ModelBasedEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.model_based.model_handler import (
    TextModelHandler,
)


@dataclass(frozen=True)
class TextSimilarityEmbeddingConfig(ModelBasedEmbeddingConfig[str, TextModelHandler]):
    cache_size: int = 0

    def __post_init__(self) -> None:
        if self.cache_size < 0:
            raise InvalidInputException("cache_size must be non-negative")
