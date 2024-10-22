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

import structlog
from google.cloud import storage

from superlinked.framework.blob.blob_handler import BlobHandler

logger = structlog.getLogger()


class GcsBlobHandler(BlobHandler):
    def __init__(self, bucket: str) -> None:
        super().__init__()
        self.__destination_bucket_name = bucket
        self.__client = storage.Client()
        self._executor = ThreadPoolExecutor()
        self._logger = logger.bind(bucket=self.__destination_bucket_name)

    def upload(self, name: str, data: bytes) -> None:
        future = self._executor.submit(self._upload_sync, name, data)
        future.add_done_callback(lambda f: self._task_done_callback(f, name, data))

    def _upload_sync(self, name: str, data: bytes) -> None:
        bucket = self.__client.bucket(self.__destination_bucket_name)
        blob = bucket.blob(name)
        blob.upload_from_file(data)

    def _task_done_callback(self, future: Future, name: str, data: bytes) -> None:
        try:
            future.result()
            self._logger.debug("uploaded blob", name=name, size=len(data))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.error("upload failed", name=name, error=str(e))
