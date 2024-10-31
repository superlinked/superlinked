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
from dataclasses import dataclass

from PIL import Image
from PIL.ImageFile import ImageFile
from typing_extensions import override

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

blob_loader = BlobLoader(allow_bytes=True)


@dataclass
class ImageSpaceFieldSet(SpaceFieldSet[ImageData]):
    @override
    def _generate_space_input(self, value: PythonTypes) -> ImageData:
        if not isinstance(value, (str, ImageFile)):
            raise ValueError(
                f"Invalid type of input for {type(self).__name__}: {type(value)}"
            )
        loaded_image = blob_loader.load(value)
        opened_image: ImageFile | None = None
        if loaded_image.data:
            opened_image = Image.open(io.BytesIO(base64.b64decode(loaded_image.data)))
        return ImageData(image=opened_image, description=None)


@dataclass
class ImageDescriptionSpaceFieldSet(SpaceFieldSet[ImageData]):
    @override
    def _generate_space_input(self, value: PythonTypes) -> ImageData:
        if not isinstance(value, str):
            raise ValueError(
                f"Invalid type of input for {type(self).__name__}: {type(value)}"
            )
        return ImageData(image=None, description=value)
