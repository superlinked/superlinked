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


import base64
from urllib.parse import urlparse

import requests
from beartype.typing import Any, cast

from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.settings import Settings


class BlobLoader:
    def __init__(self, allow_bytes: bool) -> None:
        self.allow_bytes = allow_bytes

    def load(self, blob_like_input: str | Any) -> BlobInformation:
        if not isinstance(blob_like_input, str):
            raise ValueError(
                f"Blob field must contain str input, got: {type(blob_like_input).__name__}."
            )
        if self.allow_bytes:
            try:
                decoded_bytes = base64.b64decode(blob_like_input, validate=True)
                encoded_bytes = base64.b64encode(decoded_bytes)
                return BlobInformation(encoded_bytes)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        blob_path = cast(str, blob_like_input)
        is_local_path = self.is_local_path(blob_path)
        file_loader = self.load_from_local if is_local_path else self.load_from_url
        loaded_file = file_loader(blob_path)
        encoded_file = base64.b64encode(loaded_file)
        return BlobInformation(encoded_file, blob_path)

    @staticmethod
    def is_local_path(path: str) -> bool:
        return urlparse(path).scheme in ("file", "")

    @staticmethod
    def load_from_url(url: str) -> bytes:
        try:
            response = requests.get(url, timeout=Settings().REQUEST_TIMEOUT)
            response.raise_for_status()
            loaded_file: bytes | Any = response.content
        except requests.RequestException as exc:
            raise ValueError(f"Failed to load URL: {url}.") from exc
        return loaded_file

    @staticmethod
    def load_from_local(path: str) -> bytes:
        with open(path, "rb") as file:
            loaded_file = file.read()
        return loaded_file
