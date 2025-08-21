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

import mimetypes
from abc import abstractmethod
from urllib.parse import unquote, urlparse

from beartype.typing import Sequence

from superlinked.framework.blob.blob_metadata import BlobMetadata
from superlinked.framework.common.schema.blob_information import BlobInformation


class BlobHandler:
    @abstractmethod
    def upload(self, object_key: str, data: bytes, metadata: BlobMetadata | None = None) -> None:
        pass

    @abstractmethod
    async def download(self, object_keys: Sequence[str]) -> list[BlobInformation]:
        pass

    @abstractmethod
    def get_supported_cloud_storage_scheme(self) -> str:
        pass

    def calculate_metadata(self, blob_info: BlobInformation) -> BlobMetadata:
        last_url_segment = self._get_last_url_segment(blob_info.path)
        content_type = self._determine_content_type(last_url_segment)
        return BlobMetadata(content_type=content_type, original_file_name=last_url_segment)

    def _get_last_url_segment(self, url: str | None) -> str | None:
        path = urlparse(url).path

        if isinstance(path, bytes):
            path = path.decode("utf-8")

        return unquote(path).rsplit("/", 1)[-1] if path else None

    def _determine_content_type(self, last_url_segment: str | None) -> str:
        content_type = "application/octet-stream"
        if last_url_segment:
            guessed_content_type, _ = mimetypes.guess_type(last_url_segment)
            if guessed_content_type is not None:
                content_type = guessed_content_type
        return content_type
