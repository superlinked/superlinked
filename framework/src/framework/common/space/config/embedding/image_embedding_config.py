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
from enum import Enum
from pathlib import Path

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)


class ModelHandler(Enum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPEN_CLIP = "open_clip"
    MODAL = "modal"


@dataclass(frozen=True)
class ImageEmbeddingConfig(EmbeddingConfig[ImageData]):
    model_name: str
    model_cache_dir: Path | None
    model_handler: ModelHandler
    length_to_use: int

    @property
    @override
    def length(self) -> int:
        return self.length_to_use

    @override
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        return {
            "class_name": type(self).__name__,
            "model_name": self.model_name,
        }
