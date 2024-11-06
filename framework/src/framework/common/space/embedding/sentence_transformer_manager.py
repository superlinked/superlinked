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

import json
import os
from functools import lru_cache
from pathlib import Path
from time import sleep

import numpy as np
import structlog
from beartype.typing import Any, Sequence
from filelock import FileLock
from huggingface_hub import snapshot_download
from huggingface_hub.file_download import repo_folder_name
from PIL.Image import Image
from sentence_transformers import SentenceTransformer
from typing_extensions import override

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import ModelManager
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil

logger = structlog.getLogger()

MODEL_DIMENSION = "hidden_size"
MAIN_REF_FILE_PATH = "{model_folder}/refs/main"
CONFIG_FILE_PATH = "{model_folder}/snapshots/{snapshot}/config.json"
SENTENCE_TRANSFORMERS_ORG_NAME = "sentence-transformers"


class SentenceTransformerManager(ModelManager):
    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)
        self._gpu_embedding_util = GpuEmbeddingUtil(Settings().GPU_EMBEDDING_THRESHOLD)
        self._embedding_model = self._initialize_model(model_name, "cpu")
        self._bulk_embedding_model = None
        if self._gpu_embedding_util.is_gpu_embedding_enabled:
            try:
                self._bulk_embedding_model = self._initialize_model(
                    model_name,
                    self._gpu_embedding_util.gpu_device_type,
                )
            except FileNotFoundError:
                logger.exception("Cached model not found, downloading model.")
                self._bulk_embedding_model = self._initialize_model(
                    model_name,
                    self._gpu_embedding_util.gpu_device_type,
                    False,
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

    def embed_without_nones(self, inputs: Sequence[str | Image | None]) -> list[Vector]:
        return [input_ for input_ in self.embed(inputs) if input_ is not None]

    @override
    def _embed(self, inputs: list[str | Image]) -> list[list[float]] | list[np.ndarray]:
        model = self._get_embedding_model(len(inputs))
        embeddings = model.encode(inputs)  # type: ignore[arg-type]
        return embeddings.tolist()

    @classmethod
    @lru_cache(maxsize=32)
    @override
    def calculate_length(cls, model_name: str) -> int:
        cls._ensure_model_downloaded(model_name)
        try:
            if length := cls._get_length_from_cached_model(model_name):
                return length
        except (FileNotFoundError, AttributeError, json.JSONDecodeError) as e:
            logger.debug(
                f"unable to read {MODEL_DIMENSION} from config.json",
                model_name=model_name,
                reason=str(e),
            )

        embedding_model = cls._initialize_model(model_name, "cpu")
        return embedding_model.get_sentence_embedding_dimension() or len(
            embedding_model.encode("")
        )

    @classmethod
    def _get_length_from_cached_model(cls, model_name: str) -> int | None:
        with open(cls._get_local_path(model_name), encoding="utf-8") as file:
            return json.load(file).get(MODEL_DIMENSION, None)

    @classmethod
    def _get_local_path(cls, model_name: str) -> str:
        model_folder = cls._get_model_folder_path(model_name)
        with open(
            MAIN_REF_FILE_PATH.format(model_folder=model_folder), "r", encoding="utf-8"
        ) as file:
            snapshot_value = file.read().strip()
        return CONFIG_FILE_PATH.format(
            model_folder=model_folder,
            snapshot=snapshot_value,
        )

    @classmethod
    def _ensure_model_downloaded(cls, model_name: str) -> None:
        if cls._is_model_downloaded(model_name):
            return

        cache_folder = str(cls._get_cache_folder())
        lock_file_path = os.path.join(cache_folder, f"loading_{model_name}.lock")
        settings = Settings()

        max_retries = settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_MAX_RETRIES
        retry_delay = settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_RETRY_DELAY
        timeout = max((max_retries * retry_delay) - 10, 5)

        for attempt in range(max_retries):
            try:
                with FileLock(lock_file_path, timeout=timeout):
                    snapshot_download(
                        repo_id=cls._get_repo_id(model_name),
                        cache_dir=cache_folder,
                    )
                    return
            except TimeoutError:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Timeout acquiring lock"
                    f" for downloading {model_name}, retrying in {retry_delay} seconds..."
                )
                sleep(retry_delay)

        raise RuntimeError(
            f"Failed to acquire lock for downloading {model_name} after {max_retries} attempts."
        )

    @classmethod
    def _initialize_model(
        cls, model_name: str, device: str, local_files_only: bool = True
    ) -> SentenceTransformer:
        cls._ensure_model_downloaded(model_name)
        return SentenceTransformer(
            model_name,
            trust_remote_code=True,
            local_files_only=local_files_only,
            device=device,
            cache_folder=str(cls._get_cache_folder()),
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
    def _get_repo_id(cls, model_name: str) -> str:
        return (
            SENTENCE_TRANSFORMERS_ORG_NAME + "/" + model_name
            if "/" not in model_name
            else model_name
        )

    @classmethod
    def _get_model_folder_path(cls, model_name: str) -> Path:
        return cls._get_cache_folder() / repo_folder_name(
            repo_id=cls._get_repo_id(model_name), repo_type="model"
        )
