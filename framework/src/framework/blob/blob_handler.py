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

from superlinked.framework.blob.blob_metadata import BlobMetadata
from superlinked.framework.common.schema.blob_information import BlobInformation


class BlobHandler:
    @abstractmethod
    def upload(
        self, name: str, data: bytes, metadata: BlobMetadata | None = None
    ) -> None:
        pass

    def calculate_metadata(self, blob_info: BlobInformation) -> BlobMetadata:
        file_name = blob_info.path.split("/")[-1] if blob_info.path else None
        content_type = self._determine_content_type(file_name)
        return BlobMetadata(content_type=content_type, original_file_name=file_name)

    def _determine_content_type(self, file_name: str | None) -> str:
        content_type = "application/octet-stream"
        if file_name is not None:
            guessed_content_type, _ = mimetypes.guess_type(file_name)
            if guessed_content_type is not None:
                content_type = guessed_content_type
        return content_type
