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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.embedding_type import (
    EmbeddingType,
)


class TextSimilarityEmbeddingConfig(EmbeddingConfig[str]):
    def __init__(self, model_name: str, cache_size: int, length_to_use: int) -> None:
        super().__init__(EmbeddingType.TEXT, str)
        self.model_name = model_name
        self.cache_size = cache_size
        self.length_to_use = length_to_use
        if self.cache_size < 0:
            raise ValueError("cache_size must be non-negative")

    @property
    @override
    def length(self) -> int:
        return self.length_to_use

    @override
    def to_dict(self) -> dict[str, Any]:
        return super().to_dict() | {
            "model_name": self.model_name,
            "cache_size": self.cache_size,
            "length_to_use": self.length_to_use,
        }
