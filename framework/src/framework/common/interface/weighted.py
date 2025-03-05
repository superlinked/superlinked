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

from beartype.typing import Generic, TypeVar

from superlinked.framework.common.const import constants

WeightedItemT = TypeVar("WeightedItemT")


@dataclass
class Weighted(Generic[WeightedItemT]):
    item: WeightedItemT
    weight: float = constants.DEFAULT_WEIGHT

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(item={self.item}, weight={self.weight})"

    def __repr__(self) -> str:
        return self.__str__()
