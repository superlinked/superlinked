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

import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import structlog
from beartype.typing import Sequence
from google.cloud import storage
from typing_extensions import override

from superlinked.framework.blob.blob_handler import BlobHandler
from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.util.gcs_utils import GCSFileOps

logger = structlog.getLogger()


SUPPORTED_SCHEME = "gs"


class GcsBlobHandler(BlobHandler):
    def __init__(self, bucket: str, pool_size: int = constants.DEFAULT_GCS_POOL_SIZE) -> None:
        super().__init__()
        self.__bucket_name = bucket
        self._executor = ThreadPoolExecutor()
        self._logger = logger.bind(bucket=self.__bucket_name)
        self._file_ops = GCSFileOps(pool_size=pool_size)

    @override
    async def download(self, object_keys: Sequence[str]) -> list[BlobInformation]:
        downloaded_items = await self._download(object_keys)
        return [
            BlobInformation(downloaded_item, object_key)
            for object_key, downloaded_item in zip(object_keys, downloaded_items)
        ]

    async def _download(self, object_keys: Sequence[str]) -> list[bytes]:
        bucket_object_path_pairs = [self._parse_gcs_path(object_key) for object_key in object_keys]
        bucket_cache = {}

        def get_bucket(bucket_name: str) -> storage.Bucket:
            if bucket_name not in bucket_cache:
                bucket_cache[bucket_name] = self._file_ops.storage_client.bucket(bucket_name)
            return bucket_cache[bucket_name]

        download_tasks = [
            asyncio.to_thread(self.download_blob, get_bucket(bucket_name), object_path)
            for bucket_name, object_path in bucket_object_path_pairs
        ]
        return await asyncio.gather(*download_tasks)

    def download_blob(self, bucket: storage.Bucket, object_full_path: str) -> bytes:
        try:
            blob = bucket.blob(object_full_path)
            data = blob.download_as_bytes()
            self._logger.debug(
                "downloaded blob",
                key=object_full_path,
                object_full_path=object_full_path,
                bucket=bucket.name,
                size=len(data),
            )
            return data
        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.exception(
                "failed to download",
                key=object_full_path,
                bucket=bucket.name,
                error_type=type(e).__name__,
                error_details=str(e),
            )
            raise

    @override
    def get_supported_cloud_storage_scheme(self) -> str:
        return SUPPORTED_SCHEME

    def _parse_gcs_path(self, path: str) -> tuple[str, str]:
        if not path.startswith(f"{SUPPORTED_SCHEME}://"):
            return self.__bucket_name, path.strip()

        parsed = urlparse(path)
        if not parsed.netloc:
            raise InvalidInputException(f"Invalid GCS path, missing bucket: {path}")
        if not parsed.path.lstrip("/"):
            raise InvalidInputException(f"Invalid GCS path, missing object key: {path}")

        return parsed.netloc, parsed.path.lstrip("/")
