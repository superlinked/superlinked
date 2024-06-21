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


from dataclasses import dataclass, field

from beartype.typing import Any, Sequence

from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)


@dataclass
class IndexConfig:
    index_name: str
    vector_field_descriptor: VectorIndexFieldDescriptor
    field_descriptors: Sequence[IndexFieldDescriptor]
    index_params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.__indexed_field_names = [
            field_descriptor.field_name for field_descriptor in self.field_descriptors
        ]

    @property
    def indexed_field_names(self) -> Sequence[str]:
        return self.__indexed_field_names
