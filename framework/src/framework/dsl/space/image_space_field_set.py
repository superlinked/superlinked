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

from dataclasses import dataclass

import PIL
import PIL.Image
from typing_extensions import override

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.util.image_util import ImageUtil
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

blob_loader = BlobLoader(allow_bytes=True)


@dataclass
class ImageSpaceFieldSet(SpaceFieldSet[ImageData]):
    @property
    @override
    def input_type(self) -> type:
        return str

    @override
    def _generate_space_input(self, value: PythonTypes) -> ImageData:
        if not isinstance(value, (str, PIL.Image.Image)):
            raise ValueError(f"Invalid type of input for {type(self).__name__}: {type(value)}")
        loaded_image = blob_loader.load(value)
        opened_image: PIL.Image.Image | None = None
        if loaded_image.data:
            opened_image = ImageUtil.open_image(loaded_image.data)
        return ImageData(image=opened_image, description=None)


@dataclass
class ImageDescriptionSpaceFieldSet(SpaceFieldSet[ImageData]):
    @property
    @override
    def input_type(self) -> type:
        return str

    @override
    def _generate_space_input(self, value: PythonTypes) -> ImageData:
        if not isinstance(value, str):
            raise ValueError(f"Invalid type of input for {type(self).__name__}: {type(value)}")
        return ImageData(image=None, description=value)
