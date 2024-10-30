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
import tempfile
from urllib.parse import urlparse

import requests
from beartype.typing import Any, Callable, cast
from PIL.ImageFile import ImageFile

from superlinked.framework.blob.blob_handler_factory import BlobHandlerFactory
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.settings import Settings


class BlobLoader:
    def __init__(self, allow_bytes: bool) -> None:
        self.allow_bytes = allow_bytes
        self._scheme_to_load_function: dict[str, Callable[[str], bytes]] = {
            "file": BlobLoader.load_from_local,
            "": BlobLoader.load_from_local,
            "http": BlobLoader.load_from_url,
            "https": BlobLoader.load_from_url,
        }
        if handler := BlobHandlerFactory.create_blob_handler():
            self._scheme_to_load_function[
                handler.get_supported_cloud_storage_scheme()
            ] = handler.download

    def load(self, blob_like_input: str | ImageFile | Any) -> BlobInformation:
        if not isinstance(blob_like_input, str | ImageFile):
            raise ValueError(
                f"Blob field must contain str or PIL.ImageFile input, got: {type(blob_like_input).__name__}."
            )
        if isinstance(blob_like_input, ImageFile):
            with tempfile.NamedTemporaryFile(
                suffix=f".{blob_like_input.format}", delete=True
            ) as temp:
                temp_filename = temp.name
                blob_like_input.save(temp_filename)
                loaded_file = self.load_from_local(temp_filename)
            blob_like_input = base64.b64encode(loaded_file).decode("utf-8")
        if self.allow_bytes:
            try:
                decoded_bytes = base64.b64decode(blob_like_input, validate=True)
                encoded_bytes = base64.b64encode(decoded_bytes)
                return BlobInformation(encoded_bytes)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        blob_path = cast(str, blob_like_input)
        loader = self._get_loader(blob_path)
        loaded_bytes = loader(blob_path)
        encoded_bytes = base64.b64encode(loaded_bytes)
        return BlobInformation(encoded_bytes, blob_path)

    def _get_loader(self, blob_path: str) -> Callable[[str], bytes]:
        scheme = urlparse(blob_path).scheme
        file_loader = self._scheme_to_load_function.get(scheme)
        if file_loader is None:
            raise ValueError(
                f"Unsupported scheme in path: {scheme}, possible values: {self._scheme_to_load_function.keys()}"
            )
        return file_loader

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
