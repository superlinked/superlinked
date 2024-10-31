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
from functools import lru_cache
from pathlib import Path
from time import sleep

import numpy as np
import structlog
from beartype.typing import Any, Sequence
from filelock import FileLock
from huggingface_hub.file_download import (  # type:ignore[import-untyped]
    repo_folder_name,
)
from PIL.ImageFile import ImageFile
from sentence_transformers import SentenceTransformer
from typing_extensions import override

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import (
    SENTENCE_TRANSFORMERS_ORG_NAME,
    ModelManager,
)
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil

logger = structlog.getLogger()


class SentenceTransformerManager(ModelManager):
    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)
        local_files_only = self._is_model_downloaded(model_name)
        self._gpu_embedding_util = GpuEmbeddingUtil(Settings().GPU_EMBEDDING_THRESHOLD)
        self._embedding_model = self._initialize_model(
            model_name, local_files_only, "cpu"
        )
        self._bulk_embedding_model = None
        if self._gpu_embedding_util.is_gpu_embedding_enabled:
            try:
                self._bulk_embedding_model = self._initialize_model(
                    model_name,
                    local_files_only,
                    self._gpu_embedding_util.gpu_device_type,
                )
            except FileNotFoundError:
                logger.exception("Cached model not found, downloading model.")
                self._bulk_embedding_model = self._initialize_model(
                    model_name,
                    False,
                    self._gpu_embedding_util.gpu_device_type,
                )

    def _get_embedding_model(self, number_of_inputs: int) -> SentenceTransformer:
        return (
            self._bulk_embedding_model
            if self._bulk_embedding_model
            and self._gpu_embedding_util.is_above_gpu_embedding_threshold(
                number_of_inputs
            )
            else self._embedding_model
        )

    def embed_without_nones(
        self, inputs: Sequence[str | ImageFile | None]
    ) -> list[Vector]:
        return [input_ for input_ in self.embed(inputs) if input_ is not None]

    @override
    def _embed(
        self, inputs: list[str | ImageFile]
    ) -> list[list[float]] | list[np.ndarray]:
        model = self._get_embedding_model(len(inputs))
        embeddings = model.encode(inputs)  # type: ignore[arg-type]
        return embeddings.tolist()

    @classmethod
    @lru_cache(maxsize=128)
    @override
    def calculate_length(cls, model_name: str) -> int:
        # TODO FAI-2357 find better solution
        local_files_only = cls._is_model_downloaded(model_name)
        embedding_model = cls._initialize_model(model_name, local_files_only, "cpu")
        length = embedding_model.get_sentence_embedding_dimension() or len(
            embedding_model.encode("")
        )
        return length

    @classmethod
    def _initialize_model(
        cls, model_name: str, local_files_only: bool, device: str
    ) -> SentenceTransformer:
        cache_folder = str(cls._get_cache_folder())

        def load_model() -> SentenceTransformer:
            return SentenceTransformer(
                model_name,
                trust_remote_code=True,
                local_files_only=local_files_only,
                device=device,
                cache_folder=cache_folder,
            )

        if local_files_only:
            return load_model()

        lock_file_path = os.path.join(cache_folder, f"loading_{model_name}.lock")
        settings = Settings()
        max_retries = settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_MAX_RETRIES
        retry_delay = settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_RETRY_DELAY
        timeout = max((max_retries * retry_delay) - 10, 1)
        for attempt in range(max_retries):
            try:
                with FileLock(lock_file_path, timeout=timeout):
                    return load_model()
            except TimeoutError:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Timeout acquiring lock"
                    f" for {model_name}, retrying in {retry_delay} seconds..."
                )
                sleep(retry_delay)
        raise RuntimeError(
            f"Failed to acquire lock for {model_name} after {max_retries} attempts."
        )

    @classmethod
    def _is_model_downloaded(cls, model_name: str) -> bool:
        return bool(model_name) and (
            any(
                cls._is_valid_model_directory(model_dir)
                for model_dir in [
                    cls._get_cache_folder() / model_name,
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
        return cls._get_cache_folder() / repo_folder_name(
            repo_id=repo_id, repo_type="model"
        )
