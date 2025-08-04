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

from __future__ import annotations

import os
import time
from pathlib import Path
from threading import Lock

import structlog
from filelock import FileLock
from huggingface_hub import snapshot_download
from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError
from huggingface_hub.file_download import repo_folder_name
from requests.exceptions import ReadTimeout

from superlinked.framework.common.exception import (
    InvalidStateException,
    RequestTimeoutException,
)
from superlinked.framework.common.settings import settings
from superlinked.framework.common.telemetry.telemetry_registry import telemetry

logger = structlog.getLogger()

SENTENCE_TRANSFORMERS_ORG_NAME = "sentence-transformers"
DEFAULT_MODEL_CACHE_DIR = (Path.home() / ".cache" / SENTENCE_TRANSFORMERS_ORG_NAME).absolute().as_posix()


class ModelDownloader:
    _instance: ModelDownloader | None = None
    _lock: Lock = Lock()
    _download_locks: dict[str, Lock] = {}
    _download_locks_lock: Lock = Lock()
    _framework_settings = settings

    def __new__(cls) -> ModelDownloader:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._framework_settings = settings
        return cls._instance

    def get_cache_dir(self, model_cache_dir: Path | None) -> Path:
        return model_cache_dir or Path(self._framework_settings.MODEL_CACHE_DIR or DEFAULT_MODEL_CACHE_DIR)

    def ensure_model_downloaded(
        self, model_name: str, model_cache_dir: Path | None, force_download: bool = False
    ) -> Path:
        cache_dir = self.get_cache_dir(model_cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        lock_file_path = os.path.join(str(cache_dir), f"downloading_{model_name}.lock")

        # Skip early return if force_download is True
        if (
            not force_download
            and not os.path.exists(lock_file_path)
            and self._is_model_downloaded(model_name, cache_dir)
        ):
            return self._get_model_folder_path(model_name, cache_dir)

        model_lock = self._get_model_lock(model_name)
        max_retries = self._framework_settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_MAX_RETRIES
        retry_delay = self._framework_settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_RETRY_DELAY
        timeout = max(
            (max_retries * retry_delay)
            - self._framework_settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_TIMEOUT_BUFFER_SECONDS,
            self._framework_settings.SENTENCE_TRANSFORMERS_MODEL_LOCK_TIMEOUT_MIN_SECONDS,
        )
        model_lock_timeout = self._framework_settings.MODEL_LOCK_TIMEOUT_SECONDS

        if not self._acquire_lock_with_timeout(model_lock, model_lock_timeout):
            logger.warning(f"Timeout acquiring model lock for {model_name} after {model_lock_timeout} seconds")
            raise RequestTimeoutException(f"Timeout acquiring model lock for {model_name}")

        try:
            # Skip this check if force_download is True
            if not force_download and self._is_model_downloaded(model_name, cache_dir):
                return self._get_model_folder_path(model_name, cache_dir)

            for attempt in range(max_retries):
                try:
                    with FileLock(lock_file_path, timeout=timeout):
                        # Final check after acquiring the file lock, skip if force_download is True
                        if not force_download and self._is_model_downloaded(model_name, cache_dir):
                            return self._get_model_folder_path(model_name, cache_dir)
                        logger.info(f"Downloading model {model_name} to {cache_dir}")
                        with telemetry.span(
                            "model.download", attributes={"model_name": model_name, "cache_dir": str(cache_dir)}
                        ):
                            snapshot_download(repo_id=model_name, cache_dir=str(cache_dir))
                        model_path = self._get_model_folder_path(model_name, cache_dir)
                        if not model_path.exists():
                            raise InvalidStateException(
                                "Model download completed but path does not exist.", model_path=model_path
                            )

                        return model_path
                except (
                    ReadTimeout,
                    TimeoutError,
                    RequestTimeoutException,
                    HfHubHTTPError,
                    LocalEntryNotFoundError,
                ) as e:
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries}: Issue downloading {model_name}, "
                        f"retrying in {retry_delay} seconds... Error: {str(e)}"
                    )
                    time.sleep(retry_delay)

            raise RequestTimeoutException(f"Failed to download model {model_name} after {max_retries} attempts")
        finally:
            model_lock.release()

    def _acquire_lock_with_timeout(self, lock: Lock, timeout: float) -> bool:
        end_time = time.time() + timeout
        while time.time() < end_time:
            if lock.acquire(blocking=False):
                return True
            time.sleep(0.1)  # Small sleep to avoid high CPU usage
        return False

    def _get_model_lock(self, model_name: str) -> Lock:
        with self._download_locks_lock:
            if model_name not in self._download_locks:
                self._download_locks[model_name] = Lock()
            return self._download_locks[model_name]

    @classmethod
    def _is_model_downloaded(cls, model_name: str, cache_dir: Path) -> bool:
        model_paths = [
            cache_dir / model_name,
            cls._get_model_folder_path(model_name, cache_dir),
        ]
        return any(cls._is_valid_model_directory(path) for path in model_paths)

    @classmethod
    def _is_valid_model_directory(cls, directory: Path) -> bool:
        if not directory.exists():
            return False
        incomplete_downloads = list(directory.glob("*.incomplete"))
        if incomplete_downloads:
            return False
        snapshot_dir = directory / "snapshots"
        bin_files_exist = snapshot_dir.exists() and any(snapshot_dir.glob("**/*bin"))
        return bin_files_exist

    @classmethod
    def _get_model_folder_path(cls, model_name: str, cache_dir: Path) -> Path:
        return cache_dir / repo_folder_name(repo_id=model_name, repo_type="model")
