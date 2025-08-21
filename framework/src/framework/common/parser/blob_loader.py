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
from PIL.Image import Image

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
from superlinked.framework.common.util.image_util import ImageUtil

logger = structlog.getLogger()

GCS_URL_IDENTIFIER = "storage.cloud.google.com"


class BlobLoader:
    def __init__(self, allow_bytes: bool, blob_handler_config: BlobHandlerConfig | None = None) -> None:
        self.allow_bytes = allow_bytes
        self._scheme_to_load_function: dict[str, Callable[[Sequence[str]], Awaitable[list[BlobInformation]]]] = {
            "file": BlobLoader._load_from_local,
            "": BlobLoader._load_from_local,
            "http": BlobLoader._load_from_url,
            "https": BlobLoader._load_from_url,
        }
        if handler := BlobHandlerFactory.create_blob_handler(blob_handler_config):
            self._scheme_to_load_function[handler.get_supported_cloud_storage_scheme()] = handler.download

    async def load(self, blob_like_inputs: Sequence[str | Image | None | Any]) -> list[BlobInformation | None]:
        logger_to_use = logger.bind(n_blobs=len(blob_like_inputs))
        logger_to_use.info("started blob loading")
        with telemetry.span(
            "blob.load",
            attributes={
                "n_blob_like_inputs": len(blob_like_inputs),
                "allow_bytes": self.allow_bytes,
            },
        ):
            parsed_inputs = [
                self._parse(blob_input) if blob_input is not None else None for blob_input in blob_like_inputs
            ]
            parsed_to_loaded_data = await self._load_parsed_inputs(
                [parsed for parsed in parsed_inputs if parsed is not None]
            )
            results = [parsed_to_loaded_data[parsed] if parsed is not None else None for parsed in parsed_inputs]
        logger_to_use.info("finished blob loading")
        if len(results) != len(blob_like_inputs):
            raise InvalidStateException("Length mismatch: blob_infos length does not match blob_like_inputs length.")
        return results

    def _parse(self, blob_like_input: str | Image | bytes) -> str:
        if not isinstance(blob_like_input, str | Image) or not blob_like_input:
            type_text = type(blob_like_input).__name__
            if type_text == "str":
                type_text = f"empty {type_text}"
            raise InvalidInputException(
                f"Blob field must contain a non-empty str or PIL.Image.Image input, got: {type_text}."
            )
        if isinstance(blob_like_input, Image):
            return ImageUtil.encode_b64(blob_like_input)
        return blob_like_input

    async def _load_parsed_inputs(self, parsed_inputs: Sequence[str]) -> dict[str, BlobInformation]:
        loader_to_inputs: dict[Callable[[Sequence[str]], Awaitable[list[BlobInformation]]], set[str]] = defaultdict(set)
        for parsed_input in parsed_inputs:
            loader_to_inputs[self._get_loader(parsed_input)].add(parsed_input)
        loader_results = await asyncio.gather(*[loader(list(inputs)) for loader, inputs in loader_to_inputs.items()])
        return {
            parsed_input: loaded_bytes
            for inputs, loaded_data in zip(loader_to_inputs.values(), loader_results)
            for parsed_input, loaded_bytes in zip(inputs, loaded_data)
        }

    def _get_loader(self, blob_like_input: str) -> Callable[[Sequence[str]], Awaitable[list[BlobInformation]]]:
        if self._is_base64_encoded(blob_like_input):
            if not self.allow_bytes:
                logger.error("byte input not enabled", allow_bytes=self.allow_bytes)
                raise InvalidInputException("Base64 encoded input is not supported in this operation mode.")
            return self._load_from_bytes

        scheme = urlparse(blob_like_input).scheme
        file_loader = self._scheme_to_load_function.get(scheme)
        if file_loader is None:
            raise InvalidInputException(
                f"Unsupported scheme in path: {scheme}, possible values: {self._scheme_to_load_function.keys()}"
            )
        return file_loader

    def _is_base64_encoded(self, input_string: str) -> bool:
        try:
            base64.b64decode(input_string, validate=True)
            return True
        except (binascii.Error, ValueError):
            return False

    @staticmethod
    async def _load_from_local(paths: Sequence[str]) -> list[BlobInformation]:
        async def read_file(path: str) -> BlobInformation:
            async with aiofiles.open(path, "rb") as f:
                content = await f.read()
            return BlobInformation(base64.b64encode(content), path)

        return await asyncio.gather(*[read_file(path) for path in paths])

    @staticmethod
    async def _load_from_bytes(blob_like_inputs: Sequence[str]) -> list[BlobInformation]:
        return [
            BlobInformation(base64.b64encode(base64.b64decode(blob_like_input, validate=True)), None)
            for blob_like_input in blob_like_inputs
        ]

    @staticmethod
    @staticmethod
    async def _load_from_url(urls: Sequence[str]) -> list[BlobInformation]:
        async def async_fetch(session: aiohttp.ClientSession, url: str) -> BlobInformation:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)) as response:
                    response.raise_for_status()
                    BlobLoader._validate_response_content(url, response)
                    content = await response.read()
                    return BlobInformation(base64.b64encode(content), url)
            except aiohttp.ClientError as exc:
                raise UnexpectedResponseException(f"Failed to load URL: {url}.") from exc

        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[async_fetch(session, url) for url in urls])

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
