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

import os
from pathlib import Path

import numpy as np
import structlog
from beartype.typing import Any, Sequence
from huggingface_hub.file_download import (  # type:ignore[import-untyped]
    repo_folder_name,
)
from sentence_transformers import SentenceTransformer
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.embedding.embedding_cache import EmbeddingCache
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.config.text_similarity_embedding_config import (
    TextSimilarityEmbeddingConfig,
)
from superlinked.framework.common.space.normalization import L2Norm
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil

SENTENCE_TRANSFORMERS_ORG_NAME = "sentence-transformers"
SENTENCE_TRANSFORMERS_MODEL_DIR: Path = (
    Path.home() / ".cache" / SENTENCE_TRANSFORMERS_ORG_NAME
)

logger = structlog.getLogger()


class SentenceTransformerEmbedding(Embedding[str, TextSimilarityEmbeddingConfig]):

    def __init__(self, embedding_config: TextSimilarityEmbeddingConfig) -> None:
        super().__init__(embedding_config)
        local_files_only = self._is_model_downloaded(self._config.model_name)
        self._gpu_embedding_util = GpuEmbeddingUtil(Settings().GPU_EMBEDDING_THRESHOLD)
        self._embedding_model = self._initialize_model(
            self._config.model_name, local_files_only, "cpu"
        )
        self._bulk_embedding_model = None
        if self._gpu_embedding_util.is_gpu_embedding_enabled:
            try:
                self._bulk_embedding_model = self._initialize_model(
                    self._config.model_name,
                    local_files_only,
                    self._gpu_embedding_util.gpu_device_type,
                )
            except FileNotFoundError:
                logger.exception("Cached model not found, downloading model.")
                self._bulk_embedding_model = self._initialize_model(
                    self._config.model_name,
                    False,
                    self._gpu_embedding_util.gpu_device_type,
                )
        self._cache = EmbeddingCache(self._config.cache_size)
        self._normalization = L2Norm()

    @override
    def embed_multiple(
        self, inputs: Sequence[str], context: ExecutionContext
    ) -> list[Vector]:
        cache_info = self._cache.calculate_cache_info(inputs)
        new_vectors = self._embed_uncached(cache_info.inputs_to_embed)
        self._cache.update(cache_info.inputs_to_embed, new_vectors)
        combined_vectors = cache_info.combine_vectors(new_vectors)
        return combined_vectors

    def _embed_uncached(self, inputs: Sequence[str]) -> list[Vector]:
        inputs_count = len(inputs)
        if not inputs_count:
            return []
        embedding_model = self._get_embedding_model(inputs_count)
        embeddings = embedding_model.encode(list(inputs))
        return [self._to_normalized_vector(embedding) for embedding in embeddings]

    def _get_embedding_model(self, number_of_inputs: int) -> SentenceTransformer:
        return (
            self._bulk_embedding_model
            if self._bulk_embedding_model
            and self._gpu_embedding_util.is_above_gpu_embedding_threshold(
                number_of_inputs
            )
            else self._embedding_model
        )

    @override
    def embed(self, input_: str, context: ExecutionContext) -> Vector:
        return self.embed_multiple([input_], context)[0]

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @property
    @override
    def normalization(self) -> L2Norm:
        return self._normalization

    def _to_normalized_vector(self, embedding: np.ndarray) -> Vector:
        vector_input = embedding.astype(np.float64)
        vector = Vector(vector_input)
        return self._normalization.normalize(vector)

    @classmethod
    def calculate_length(cls, model_name: str) -> int:
        # TODO FAI-2357 find better solution
        local_files_only = cls._is_model_downloaded(model_name)
        embedding_model = cls._initialize_model(model_name, local_files_only, "cpu")
        length = embedding_model.get_sentence_embedding_dimension() or 0
        return length

    @classmethod
    def _initialize_model(
        cls, model_name: str, local_files_only: bool, device: str
    ) -> SentenceTransformer:
        return SentenceTransformer(
            model_name,
            trust_remote_code=True,
            local_files_only=local_files_only,
            device=device,
            cache_folder=str(SENTENCE_TRANSFORMERS_MODEL_DIR),
        )

    @classmethod
    def _is_model_downloaded(cls, model_name: str) -> bool:
        return bool(model_name) and (
            any(
                cls._is_valid_model_directory(model_dir)
                for model_dir in [
                    SENTENCE_TRANSFORMERS_MODEL_DIR / model_name,
                    cls._get_model_folder_path(model_name),
                ]
            )
        )

    @classmethod
    def _is_valid_model_directory(cls, directory: Path) -> bool:
        if not directory.exists():
            return False
        incomplete_downloads = list(directory.glob("*.incomplete"))
        cls._delete_incomplete_downloads(incomplete_downloads)
        return not incomplete_downloads

    @classmethod
    def _delete_incomplete_downloads(cls, incomplete_downloads: list[Any]) -> None:
        for incomplete_download in incomplete_downloads:
            os.remove(incomplete_download)

    @classmethod
    def _get_model_folder_path(cls, model_name: str) -> Path:
        repo_id = (
            SENTENCE_TRANSFORMERS_ORG_NAME + "/" + model_name
            if "/" not in model_name
            else model_name
        )
        return SENTENCE_TRANSFORMERS_MODEL_DIR / repo_folder_name(
            repo_id=repo_id, repo_type="model"
        )
