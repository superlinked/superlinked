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

FALLBACK_IMAGE_FORMAT = "PNG"
RGB = "RGB"

# Standard input dimensions (224x224) for vision models that optimize for both performance and accuracy
EMBEDDING_IMAGE_SIZE = (224, 224)


class ImageUtil:
    @staticmethod
    def encode_b64(image: PIL.Image.Image) -> str:
        return base64.b64encode(ImageUtil.encode_bytes(image)).decode("utf-8")

    @staticmethod
    def encode_bytes(image: PIL.Image.Image, image_format: str | None = None, quality: int = 100) -> bytes:
        format_to_use = image_format or image.format or FALLBACK_IMAGE_FORMAT
        with io.BytesIO() as buffer:
            image.save(buffer, format=format_to_use, quality=quality)
            encoded_bytes = buffer.getvalue()
        return encoded_bytes

    @staticmethod
    def open_image(data: bytes) -> PIL.Image.Image:
        return PIL.Image.open(io.BytesIO(base64.b64decode(data)))

    @staticmethod
    def open_local_image_file(dir_path: str, file_name: str) -> PIL.Image.Image:
        return PIL.Image.open(os.path.join(dir_path, file_name))

    @staticmethod
    def resize_for_embedding(image: PIL.Image.Image) -> PIL.Image.Image:
        return image.convert(RGB).resize(EMBEDDING_IMAGE_SIZE)
