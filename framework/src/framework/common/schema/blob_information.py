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


@dataclass(frozen=True)
class BlobInformation:
    data: bytes | None = None
    path: str | None = None

    def __post_init__(self) -> None:
        if self.data is None and self.path is None:
            raise ValueError(
                f"{type(self).__name__} must have a non-null data or path."
            )

    @property
    def original(self) -> str:
        return_value = ""
        if self.path is not None:
            return_value = self.path
        elif self.data is not None:
            return_value = self.data.decode("utf-8")
        return return_value
