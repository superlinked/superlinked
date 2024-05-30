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
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import NPArray, Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization

CATEGORICAL_ENCODING_VALUE: int = 1


class CategoricalSimilarityParams:
    def __init__(
        self,
        categories: list[str],
        uncategorized_as_category: bool,
        negative_filter: float = 0.0,
    ):
        self.categories: list[str] = categories
        self.uncategorized_as_category: bool = uncategorized_as_category
        self.negative_filter: float = negative_filter


class CategoricalSimilarityEmbedding(Embedding[list[str]], HasLength):
    def __init__(
        self,
        categorical_similarity_param: CategoricalSimilarityParams,
        normalization: Normalization,
    ) -> None:
        self.categorical_similarity_param: CategoricalSimilarityParams = (
            categorical_similarity_param
        )
        self.__length: int = (
            len(self.categorical_similarity_param.categories) + 1
        )  # last bin reserved for 'other'
        self.__normalization: Normalization = normalization
        self.__category_index_map: dict[str, int] = {
            elem: i
            for i, elem in enumerate(self.categorical_similarity_param.categories)
        }
        self.other_category_index: int | None = (
            self.__length - 1
            if self.categorical_similarity_param.uncategorized_as_category
            else None
        )

    @override
    def embed(self, input_: list[str], context: ExecutionContext) -> Vector:
        one_hot_encoding: NPArray = self.__n_hot_encode(
            input_, context.is_query_context()
        )
        return Vector(one_hot_encoding)

    def __n_hot_encode(self, category_list: list[str], is_query: bool) -> NPArray:
        n_hot_encoding: NPArray = np.full(
            self.__length,
            0 if is_query else self.categorical_similarity_param.negative_filter,
            dtype=np.float32,
        )
        category_indices: Sequence[int] = self.__get_category_indices(category_list)
        if category_indices:
            n_hot_encoding[category_indices] = self.__get_normalized_vector_input()
        return n_hot_encoding

    def __get_normalized_vector_input(self) -> float:
        vector_input = np.array([CATEGORICAL_ENCODING_VALUE])
        vector = Vector(vector_input).normalize(self.normalization.norm(vector_input))
        return vector.value[0]

    def __get_category_indices(self, text_input: list[str]) -> list[int]:
        return list(
            {
                category_index
                for category_value in text_input
                if (category_index := self.__get_index_for_category(category_value))
                is not None
            }
        )

    def __get_index_for_category(self, category: str) -> int | None:
        return self.__category_index_map.get(
            category,
            self.other_category_index,
        )

    @property
    @override
    def length(self) -> int:
        return self.__length

    @property
    def category_index_map(self) -> dict[str, int]:
        return self.__category_index_map

    @property
    def categories(self) -> list[str]:
        return self.categorical_similarity_param.categories

    @property
    def negative_filter(self) -> float:
        return self.categorical_similarity_param.negative_filter

    @property
    def uncategorized_as_category(self) -> bool:
        return self.categorical_similarity_param.uncategorized_as_category

    @property
    def normalization(self) -> Normalization:
        return self.__normalization
