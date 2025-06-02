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
from typing_extensions import Union, override

from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)
from superlinked.framework.common.space.embedding.hugging_face_manager import (
    HuggingFaceManager,
)
from superlinked.framework.common.space.embedding.modal_manager import ModalManager
from superlinked.framework.common.space.embedding.sentence_transformer_manager import (
    SentenceTransformerManager,
)

TextModelManager = Union[SentenceTransformerManager, HuggingFaceManager, ModalManager]


class TextModelHandler(Enum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    HUGGING_FACE = "hugging_face"
    MODAL = "modal"

    def create_manager(self, model_name: str, model_cache_dir: Path | None = None) -> TextModelManager:
        match self:
            case TextModelHandler.SENTENCE_TRANSFORMERS:
                return SentenceTransformerManager(model_name, model_cache_dir)
            case TextModelHandler.HUGGING_FACE:
                return HuggingFaceManager(model_name, model_cache_dir)
            case TextModelHandler.MODAL:
                return ModalManager(model_name, model_cache_dir)
            case _:
                raise ValueError(f"Unsupported model handler: {self}")


@dataclass(frozen=True)
class TextSimilarityEmbeddingConfig(EmbeddingConfig[str]):
    model_name: str
    model_cache_dir: Path | None
    cache_size: int
    length_to_use: int
    text_model_handler: TextModelHandler = TextModelHandler.SENTENCE_TRANSFORMERS

    def __post_init__(self) -> None:
        if self.cache_size < 0:
            raise ValueError("cache_size must be non-negative")

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
