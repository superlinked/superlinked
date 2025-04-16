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


class ImageUtil:
    @staticmethod
    def encode_b64(image: PIL.Image.Image) -> str:
        with io.BytesIO() as buffer:
            image.save(buffer, format=image.format or FALLBACK_IMAGE_FORMAT)
            encoded_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return encoded_str

    @staticmethod
    def open_image(data: bytes) -> PIL.Image.Image:
        return PIL.Image.open(io.BytesIO(base64.b64decode(data)))

    @staticmethod
    def open_local_image_file(dir_path: str, file_name: str) -> PIL.Image.Image:
        return PIL.Image.open(os.path.join(dir_path, file_name))
