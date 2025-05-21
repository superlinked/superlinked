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

from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)


@dataclass(frozen=True)
class CategoricalSimilarityEmbeddingConfig(EmbeddingConfig[list[str]]):
    categories: Sequence[str]
    uncategorized_as_category: bool
    negative_filter: float = 0.0

    @property
    @override
    def length(self) -> int:
        return len(self.categories) + 1

    @override
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        return {
            "class_name": type(self).__name__,
            "transformation_config": set(self.categories),
            "uncategorized_as_category": self.uncategorized_as_category,
            "negative_filter": self.negative_filter,
        }

    @override
    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                tuple(self.categories),
                self.uncategorized_as_category,
                self.negative_filter,
            )
        )
