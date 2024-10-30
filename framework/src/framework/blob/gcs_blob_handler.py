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

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict
from urllib.parse import urlparse

import structlog
from beartype.typing import Any
from google.cloud import storage
from typing_extensions import override

from superlinked.framework.blob.blob_handler import BlobHandler
from superlinked.framework.blob.blob_metadata import BlobMetadata

logger = structlog.getLogger()

SUPPORTED_SCHEME = "gs"


class GcsBlobHandler(BlobHandler):
    def __init__(self, bucket: str) -> None:
        super().__init__()
        self.__bucket_name = bucket
        self.__client = storage.Client()
        self._executor = ThreadPoolExecutor()
        self._logger = logger.bind(bucket=self.__bucket_name)

    @override
    def upload(
        self, object_key: str, data: bytes, metadata: BlobMetadata | None = None
    ) -> None:
        future = self._executor.submit(self._upload_sync, object_key, data, metadata)
        future.add_done_callback(
            lambda f: self._task_done_callback(f, object_key, data)
        )

    @override
    def download(self, object_key: str) -> bytes:
        try:
            bucket_name, object_full_path = self._parse_gcs_path(object_key)
            bucket = self.__client.bucket(bucket_name)
            blob = bucket.blob(object_full_path)
            data = blob.download_as_bytes()
            self._logger.debug(
                "downloaded blob",
                key=object_key,
                object_full_path=object_full_path,
                bucket=bucket_name,
                size=len(data),
            )
            return data
        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.exception(
                "failed to download",
                key=object_key,
                error_type=type(e).__name__,
                error_details=str(e),
            )
            raise

    @override
    def get_supported_cloud_storage_scheme(self) -> str:
        return SUPPORTED_SCHEME

    def _upload_sync(
        self, object_key: str, data: bytes, metadata: BlobMetadata | None
    ) -> None:
        bucket = self.__client.bucket(self.__bucket_name)
        blob = bucket.blob(object_key)
        upload_args: dict[str, Any] = {"data": data}
        if metadata is not None:
            upload_args.update({"content_type": metadata.content_type})
            blob.metadata = asdict(metadata)
        blob.upload_from_string(**upload_args)

    def _task_done_callback(self, future: Future, object_key: str, data: bytes) -> None:
        try:
            future.result()
            self._logger.debug("uploaded blob", object_key=object_key, size=len(data))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.exception(
                "upload failed",
                object_key=object_key,
                error_type=type(e).__name__,
                error_details=str(e),
            )

    def _parse_gcs_path(self, path: str) -> tuple[str, str]:
        if not path.startswith(f"{SUPPORTED_SCHEME}://"):
            return self.__bucket_name, path.strip()

        parsed = urlparse(path)
        if not parsed.netloc:
            raise ValueError(f"Invalid GCS path, missing bucket: {path}")
        if not parsed.path.lstrip("/"):
            raise ValueError(f"Invalid GCS path, missing object key: {path}")

        return parsed.netloc, parsed.path.lstrip("/")
