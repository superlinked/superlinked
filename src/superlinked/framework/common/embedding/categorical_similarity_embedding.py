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


import numpy as np
import numpy.typing as npt

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength


class CategoricalSimilarityEmbedding(HasLength):
    def __init__(self, categories: list[str], negative_filter: float) -> None:
        self.__length: int = len(categories) + 1  # We reserve the last bin for 'other'
        self.__categories: list[str] = categories
        self.__negative_filter: float = negative_filter

    def transform(self, text: str) -> Vector:
        one_hot_encoding: npt.NDArray[np.float64] = self.__one_hot_encode(text)
        return Vector(one_hot_encoding)

    def __one_hot_encode(self, text: str) -> npt.NDArray[np.float64]:
        one_hot_encoding: npt.NDArray[np.float64] = np.full(
            self.__length, self.__negative_filter, dtype=np.float32
        )
        category_index: int = self.__get_category_index(text)
        one_hot_encoding[category_index] = 1
        return one_hot_encoding

    def __get_category_index(self, text: str) -> int:
        return (
            self.__categories.index(text)
            if text in self.__categories
            else self.__length - 1
        )

    @property
    def length(self) -> int:
        return self.__length
