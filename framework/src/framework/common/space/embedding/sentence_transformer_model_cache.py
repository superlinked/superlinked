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

import structlog
from beartype.typing import Any, Sequence
from filelock import FileLock
from huggingface_hub import snapshot_download
from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError
from huggingface_hub.file_download import repo_folder_name
from requests.exceptions import ReadTimeout
from sentence_transformers import SentenceTransformer

from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import (
    SENTENCE_TRANSFORMERS_ORG_NAME,
)
from superlinked.framework.common.util.execution_timer import time_execution
from superlinked.framework.common.util.gpu_embedding_util import (
    CPU_DEVICE_TYPE,
    GpuEmbeddingUtil,
)

logger = structlog.getLogger()

MODEL_DIMENSION = "hidden_size"
MAIN_REF_FILE_PATH = "{model_folder}/refs/main"
CONFIG_FILE_PATH = "{model_folder}/snapshots/{snapshot}/config.json"


class SentenceTransformerModelCache:
    @classmethod
    @lru_cache(maxsize=Settings().SUPERLINKED_MODEL_CACHE_SIZE)
    @time_execution
    def initialize_model(
        cls,
        model_name: str,
        device: str,
        model_cache_dir: Path,
    ) -> SentenceTransformer:
        cls._ensure_model_downloaded(model_name, model_cache_dir)
        model_kwargs = cls._get_model_kwargs(device)
        try:
            return SentenceTransformer(
                model_name_or_path=model_name,
                trust_remote_code=True,
                device=device,
                cache_folder=str(model_cache_dir),
                local_files_only=True,
                model_kwargs=model_kwargs,
            )
        except (OSError, AttributeError, TypeError):
            logger.exception("Failed to use downloaded model, re-downloading.")
            return SentenceTransformer(
                model_name_or_path=model_name,
                trust_remote_code=True,
                device=device,
                cache_folder=str(model_cache_dir),
                local_files_only=False,
                model_kwargs=model_kwargs,
            )

    @classmethod
    def _get_model_kwargs(cls, device: str) -> dict[str, Any]:
        if GpuEmbeddingUtil.should_use_full_precision(device):
            return {}
        return {"torch_dtype": "float16"}

    @classmethod
    @lru_cache(maxsize=32)
    def calculate_length(cls, model_name: str, model_cache_dir: Path) -> int:
        cls._ensure_model_downloaded(model_name, model_cache_dir)
        try:
            if length := cls._get_length_from_cached_model(model_name, model_cache_dir):
                return length
        except (FileNotFoundError, AttributeError, json.JSONDecodeError) as e:
            logger.debug(
                f"unable to read {MODEL_DIMENSION} from config.json",
                model_name=model_name,
                reason=str(e),
            )

        embedding_model = cls.initialize_model(model_name, CPU_DEVICE_TYPE, model_cache_dir)
        return embedding_model.get_sentence_embedding_dimension() or len(embedding_model.encode(""))

    @classmethod
    def _ensure_model_downloaded(cls, model_name: str, model_cache_dir: Path) -> None:
        if cls._is_model_downloaded(model_name, model_cache_dir):
            return

        cache_folder = str(model_cache_dir)
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
            except (ReadTimeout, TimeoutError, HfHubHTTPError, LocalEntryNotFoundError) as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Timeout acquiring lock"
                    f" for downloading {model_name}, retrying in {retry_delay} seconds..."
                    f" Error: {str(e)}"
                )
                sleep(retry_delay)

        raise RuntimeError(f"Failed to acquire lock for downloading {model_name} after {max_retries} attempts.")

    @classmethod
    def _is_model_downloaded(cls, model_name: str, model_cache_dir: Path) -> bool:
        return bool(model_name) and (
            any(
                cls._is_valid_model_directory(model_dir)
                for model_dir in [
                    model_cache_dir / model_name,
                    cls._get_model_folder_path(model_name, model_cache_dir),
                ]
            )
        )

    @classmethod
    def _is_valid_model_directory(cls, directory: Path) -> bool:
        if not directory.exists():
            return False
        incomplete_downloads = list[Path](directory.glob("*.incomplete"))
        cls._delete_incomplete_downloads(incomplete_downloads)
        return not incomplete_downloads

    @classmethod
    def _delete_incomplete_downloads(cls, incomplete_downloads: Sequence[Path]) -> None:
        for incomplete_download in incomplete_downloads:
            os.remove(incomplete_download)

    @classmethod
    def _get_repo_id(cls, model_name: str) -> str:
        return SENTENCE_TRANSFORMERS_ORG_NAME + "/" + model_name if "/" not in model_name else model_name

    @classmethod
    def _get_model_folder_path(cls, model_name: str, model_cache_dir: Path) -> Path:
        return model_cache_dir / repo_folder_name(repo_id=cls._get_repo_id(model_name), repo_type="model")

    @classmethod
    def _get_length_from_cached_model(cls, model_name: str, model_cache_dir: Path) -> int | None:
        with open(cls._get_local_path(model_name, model_cache_dir), encoding="utf-8") as file:
            return json.load(file).get(MODEL_DIMENSION, None)

    @classmethod
    def _get_local_path(cls, model_name: str, model_cache_dir: Path) -> str:
        model_folder = cls._get_model_folder_path(model_name, model_cache_dir)
        with open(MAIN_REF_FILE_PATH.format(model_folder=model_folder), "r", encoding="utf-8") as file:
            snapshot_value = file.read().strip()
        return CONFIG_FILE_PATH.format(
            model_folder=model_folder,
            snapshot=snapshot_value,
        )
