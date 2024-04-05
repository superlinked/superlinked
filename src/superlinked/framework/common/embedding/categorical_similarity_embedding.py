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

CATEGORICAL_ENCODING_VALUE: int = 1


class CategoricalSimilarityEmbedding(HasLength):
    def __init__(
        self,
        categories: list[str],
        negative_filter: float,
        uncategorised_as_category: bool,
    ) -> None:
        self.__length: int = len(categories) + 1  # We reserve the last bin for 'other'
        self.__categories: list[str] = categories
        self.__negative_filter: float = negative_filter
        self.__uncategorised_as_category: bool = uncategorised_as_category

    def transform(self, text: str, is_query: bool) -> Vector:
        one_hot_encoding: npt.NDArray[np.float64] = self.__one_hot_encode(
            text, is_query
        )
        return Vector(one_hot_encoding)

    def __one_hot_encode(self, text: str, is_query: bool) -> npt.NDArray[np.float64]:
        one_hot_encoding: npt.NDArray[np.float64] = np.full(
            self.__length, 0 if is_query else self.__negative_filter, dtype=np.float32
        )
        category_index: int | None = self.__get_category_index(text, is_query)
        if category_index is not None:
            one_hot_encoding[category_index] = CATEGORICAL_ENCODING_VALUE
        return one_hot_encoding

    def __get_category_index(self, text: str, is_query: bool) -> int | None:
        if text in self.__categories:
            return self.__categories.index(text)
        return (
            (self.__length - 1)
            if (self.__uncategorised_as_category or is_query)
            else None
        )

    @property
    def length(self) -> int:
        return self.__length
