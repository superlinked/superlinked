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
import io
import os

import PIL
import PIL.Image
from beartype.typing import IO
from PIL._typing import StrOrBytesPath

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.settings import image_settings

PILImage = PIL.Image.Image
CONVERSION_MODE = "RGB"


class ImageUtil:
    @staticmethod
    def encode_bytes(image: PILImage, image_format: str | None = None, quality: int = 100) -> bytes:
        format_to_use = image_format or image.format or image_settings.IMAGE_FORMAT
        with io.BytesIO() as buffer:
            image.save(buffer, format=format_to_use, quality=quality)
            encoded_bytes = buffer.getvalue()
        return encoded_bytes

    @staticmethod
    def open(fp: StrOrBytesPath | IO[bytes]) -> PILImage:
        return PIL.Image.open(fp)

    @staticmethod
    def open_image(data: bytes | str) -> PILImage:
        if isinstance(data, str):
            data = base64.b64decode(data, validate=True)
        try:
            return ImageUtil.open(io.BytesIO(data))
        except OSError as e:
            raise InvalidInputException(f"Failed to open image ({str(data)}).") from e

    @staticmethod
    def open_local_image_file(dir_path: str, file_name: str) -> PILImage:
        try:
            return ImageUtil.open(os.path.join(dir_path, file_name))
        except OSError as e:
            raise InvalidInputException(f"Failed to open image ({dir_path}/{file_name}).") from e

    @staticmethod
    def resize(image: PILImage) -> bytes:
        resized_image = image.convert(CONVERSION_MODE).resize(
            (image_settings.RESIZE_IMAGE_WIDTH, image_settings.RESIZE_IMAGE_HEIGHT)
        )
        return ImageUtil.encode_bytes(resized_image, image_settings.IMAGE_FORMAT, image_settings.IMAGE_QUALITY)
