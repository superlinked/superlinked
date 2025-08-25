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

from typing_extensions import override

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.util.image_util import PILImage
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

blob_loader = BlobLoader(allow_bytes=True)


@dataclass
class ImageSpaceFieldSet(SpaceFieldSet[ImageData]):
    @property
    @override
    def input_type(self) -> type:
        return str

    @override
    async def _generate_space_input(self, value: PythonTypes) -> ImageData:
        if not isinstance(value, (str, PILImage)):
            raise InvalidStateException(f"Invalid type of input for {type(self).__name__}.", input_type=type(value))
        loaded_image = loaded_image = (await blob_loader.load([value]))[0]
        opened_image: PILImage | None = loaded_image.data if loaded_image and loaded_image.data else None
        return ImageData(image=opened_image, description=None)


@dataclass
class ImageDescriptionSpaceFieldSet(SpaceFieldSet[ImageData]):
    @property
    @override
    def input_type(self) -> type:
        return str

    @override
    async def _generate_space_input(self, value: PythonTypes) -> ImageData:
        if not isinstance(value, str):
            raise InvalidStateException(f"Invalid type of input for {type(self).__name__}.", input_type=type(value))
        return ImageData(image=None, description=value)
