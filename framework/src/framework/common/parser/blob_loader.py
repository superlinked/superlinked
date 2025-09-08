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
import base64
import binascii
from collections import defaultdict
from urllib.parse import urlparse

import aiofiles
import aiohttp
import structlog
from beartype.typing import Any, Awaitable, Callable, Sequence

from superlinked.framework.blob.blob_handler_factory import (
    BlobHandlerConfig,
    BlobHandlerFactory,
)
from superlinked.framework.common.exception import (
    InvalidInputException,
    InvalidStateException,
    UnexpectedResponseException,
)
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.settings import settings
from superlinked.framework.common.telemetry.telemetry_registry import telemetry
from superlinked.framework.common.util.image_util import ImageUtil, PILImage

logger = structlog.getLogger()

GCS_URL_IDENTIFIER = "storage.cloud.google.com"


class BlobLoader:
    def __init__(self, blob_handler_config: BlobHandlerConfig | None = None) -> None:
        self._scheme_to_load_function: dict[str, Callable[[Sequence[str]], Awaitable[list[BlobInformation]]]] = {
            "file": BlobLoader._load_from_local,
            "": BlobLoader._load_from_local,
            "http": self._load_from_url,
            "https": self._load_from_url,
        }
        if handler := BlobHandlerFactory.create_blob_handler(blob_handler_config):
            self._scheme_to_load_function[handler.get_supported_cloud_storage_scheme()] = handler.download
        self._http_session: aiohttp.ClientSession | None = None

    def _get_http_session(self) -> aiohttp.ClientSession:
        if self._http_session is None or self._http_session.closed:
            self._http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT))
        return self._http_session

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._http_session is not None and not self._http_session.closed:
            await self._http_session.close()
            self._http_session = None

    async def load(self, blob_like_inputs: Sequence[str | PILImage | None | Any]) -> list[BlobInformation | None]:
        with telemetry.span(
            "blob.load",
            attributes={"n_blob_like_inputs": len(blob_like_inputs)},
        ):
            for blob_like_input in blob_like_inputs:
                self._validate_blob_input(blob_like_input)
            non_none_inputs = [blob_like_input for blob_like_input in blob_like_inputs if blob_like_input is not None]
            loaded_blob_infos = await self._load_parsed_inputs(non_none_inputs)
            results = self._reconstruct_results(blob_like_inputs, loaded_blob_infos)
        if len(results) != len(blob_like_inputs):
            raise InvalidStateException("Length mismatch: blob_infos length does not match blob_like_inputs length.")
        return results

    def _reconstruct_results(
        self, blob_like_inputs: Sequence[str | PILImage | None], loaded_blob_infos: Sequence[BlobInformation | None]
    ) -> list[BlobInformation | None]:
        none_positions = {i for i, blob_like_input in enumerate(blob_like_inputs) if blob_like_input is None}
        non_none_iter = iter(loaded_blob_infos)
        return [None if i in none_positions else next(non_none_iter) for i in range(len(blob_like_inputs))]

    def _validate_blob_input(self, blob_like_input: str | PILImage | Any) -> None:
        if blob_like_input is not None and not isinstance(blob_like_input, str | PILImage):
            type_text = type(blob_like_input).__name__
            if type_text == "str":
                type_text = f"empty {type_text}"
            raise InvalidInputException(
                f"Blob field must contain a non-empty str or PIL.Image.Image input, got: {type_text}."
            )

    async def _load_parsed_inputs(self, parsed_inputs: Sequence[str | PILImage]) -> list[BlobInformation | None]:
        loader_to_string_positions = self.__init_loader_to_string_positions(parsed_inputs)
        results: list[BlobInformation | None] = [None] * len(parsed_inputs)

        loader_tasks = []
        loader_info = []
        for loader, string_positions in loader_to_string_positions.items():
            unique_strings = list(string_positions.keys())
            loader_tasks.append(loader(unique_strings))
            loader_info.append((unique_strings, string_positions))
        blob_infos_lists = await asyncio.gather(*loader_tasks)
        for (unique_strings, string_positions), blob_infos in zip(loader_info, blob_infos_lists):
            for unique_string, blob_info in zip(unique_strings, blob_infos):
                for position in string_positions[unique_string]:
                    results[position] = blob_info
        index_pil_image_or_blob_info_pairs = [(i, blob) for i, blob in enumerate(results) if blob is not None] + [
            (i, parsed_input) for i, parsed_input in enumerate(parsed_inputs) if isinstance(parsed_input, PILImage)
        ]
        resized_blobs = await asyncio.gather(
            *[asyncio.to_thread(self.__resize, blob) for _, blob in index_pil_image_or_blob_info_pairs]
        )
        for (i, _), resized_blob in zip(index_pil_image_or_blob_info_pairs, resized_blobs):
            results[i] = resized_blob
        return results

    @staticmethod
    async def _load_from_local(paths: Sequence[str]) -> list[BlobInformation]:
        async def read_file(path: str) -> BlobInformation:
            try:
                async with aiofiles.open(path, "rb") as f:
                    content = await f.read()
            except (OSError, FileNotFoundError) as e:
                raise InvalidInputException(f"Failed to open image {path}.") from e
            return BlobInformation(content, path)

        return await asyncio.gather(*[read_file(path) for path in paths])

    @staticmethod
    async def _load_from_bytes(blob_like_inputs: Sequence[str]) -> list[BlobInformation]:
        return [BlobInformation(base64.b64decode(blob_like_input), None) for blob_like_input in blob_like_inputs]

    async def _load_from_url(self, urls: Sequence[str]) -> list[BlobInformation]:
        async def fetch(url: str) -> BlobInformation:
            async with self._get_http_session().get(url) as response:
                response.raise_for_status()
                BlobLoader._validate_response_content(url, response)
                content = await response.read()
                return BlobInformation(content, url)

        return await asyncio.gather(*[fetch(url) for url in urls])

    @staticmethod
    def _validate_response_content(url: str, response: aiohttp.ClientResponse) -> None:
        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type:
            return
        if GCS_URL_IDENTIFIER in url:
            raise InvalidInputException(
                f"Unable to access non-public Google Cloud Storage bucket: {url}. "
                "Configure GCS blob handler to access private buckets."
            )
        raise UnexpectedResponseException(f"Unexpected HTML content for URL: {url}")

    def __resize(self, image_data: BlobInformation | PILImage) -> BlobInformation:
        if isinstance(image_data, BlobInformation):
            if image_data.data is None:
                raise InvalidStateException("Blob data is None, cannot resize.")
            image = ImageUtil.open_image(image_data.data)
            path = image_data.path
        else:
            image = image_data
            path = None
        return BlobInformation(ImageUtil.resize(image), path)

    def __init_loader_to_string_positions(
        self, parsed_inputs: Sequence[str | PILImage]
    ) -> dict[Callable[[Sequence[str]], Awaitable[list[BlobInformation]]], dict[str, list[int]]]:
        loader_to_string_positions: dict[
            Callable[[Sequence[str]], Awaitable[list[BlobInformation]]], dict[str, list[int]]
        ] = defaultdict(lambda: defaultdict(list))
        for i, parsed_input in enumerate(parsed_inputs):
            if isinstance(parsed_input, str):
                loader = self.__get_loader(parsed_input)
                loader_to_string_positions[loader][parsed_input].append(i)
        return loader_to_string_positions

    def __get_loader(self, blob_like_input: str) -> Callable[[Sequence[str]], Awaitable[list[BlobInformation]]]:
        if self.__is_base64_encoded(blob_like_input):
            return self._load_from_bytes

        scheme = urlparse(blob_like_input).scheme
        file_loader = self._scheme_to_load_function.get(scheme)
        if file_loader is None:
            raise InvalidInputException(
                f"Unsupported scheme in path: {scheme}, possible values: {self._scheme_to_load_function.keys()}"
            )
        return file_loader

    def __is_base64_encoded(self, input_string: str) -> bool:
        try:
            base64.b64decode(input_string, validate=True)
            return True
        except (binascii.Error, ValueError):
            return False
