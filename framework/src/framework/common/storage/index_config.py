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

from beartype.typing import Sequence

from superlinked.framework.common.storage.search_index.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)


@dataclass
class IndexConfig:
    index_name: str
    vector_field_descriptor: VectorIndexFieldDescriptor
    field_descriptors: Sequence[IndexFieldDescriptor]

    def __post_init__(self) -> None:
        field_descriptors = list(self.field_descriptors)
        self.__indexed_field_names = [field_descriptor.field_name for field_descriptor in field_descriptors]

    @property
    def all_field_descriptors(self) -> Sequence[IndexFieldDescriptor]:
        return [self.vector_field_descriptor] + list(self.field_descriptors)

    @property
    def indexed_field_names(self) -> Sequence[str]:
        return self.__indexed_field_names
