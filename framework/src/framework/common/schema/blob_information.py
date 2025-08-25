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
from dataclasses import dataclass

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.util.image_util import ImageUtil, PILImage


@dataclass(frozen=True)
class BlobInformation:
    data: PILImage | None = None
    path: str | None = None

    def __post_init__(self) -> None:
        if self.data is None and self.path is None:
            raise InvalidInputException(f"{type(self).__name__} must have a non-null data or path.")

    @property
    def original(self) -> str:
        return_value = ""
        if self.path is not None:
            return_value = self.path
        elif self.data is not None:
            encoded_image = ImageUtil.encode_bytes(self.data)
            return_value = base64.b64encode(encoded_image).decode("utf-8")
        return return_value
