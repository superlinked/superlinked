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


import math

import numpy as np
from beartype.typing import Mapping, Sequence
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import NPArray, Vector, VectorItemT
from superlinked.framework.common.space.config.embedding.categorical_similarity_embedding_config import (
    CategoricalSimilarityEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.embedding import InvertibleEmbedding
from superlinked.framework.common.space.embedding.model_based.embedding_engine_manager import (
    EmbeddingEngineManager,
)
from superlinked.framework.common.util.collection_util import CollectionUtil


class CategoricalSimilarityEmbedding(InvertibleEmbedding[list[str], CategoricalSimilarityEmbeddingConfig]):

    def __init__(
        self, embedding_config: CategoricalSimilarityEmbeddingConfig, embedding_engine_manager: EmbeddingEngineManager
    ) -> None:
        super().__init__(embedding_config, embedding_engine_manager)
        self._other_category_name = (
            f"{sorted(list(self._config.categories), key=len)[-1] if self._config.categories else ''}_"
        )
        self._other_category_index: int | None = self.length - 1 if self._config.uncategorized_as_category else None
        self._category_index_map: dict[str, int] = {elem: i for i, elem in enumerate(self._config.categories)}
        self._default_n_hot_encoding = np.full(self.length, self._config.negative_filter, dtype=VectorItemT)

    @override
    async def embed(self, input_: list[str], context: ExecutionContext) -> Vector:
        n_hot_encoding: NPArray = self._n_hot_encode(input_, context.is_query_context)
        negative_filter_indices = set(i for i in range(self.length) if i not in self._get_category_indices(input_))
        return Vector(n_hot_encoding, negative_filter_indices)

    @override
    def inverse_embed(self, vector: Vector, context: ExecutionContext) -> list[str]:
        return [
            self._config.categories[i] if i < len(self._config.categories) else self._other_category_name
            for i in vector.non_negative_filter_indices
            if vector.value[i] != constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE
        ]

    def get_categorical_encoding_value(self, len_category_list: int, is_query: bool) -> float:
        sqrt_len_config_categories: float = math.sqrt(len(self._config.categories))
        return sqrt_len_config_categories / (len_category_list or 1.0) if is_query else 1.0 / sqrt_len_config_categories

    def _n_hot_encode(self, category_list: Sequence[str], is_query: bool) -> NPArray:
        n_hot_encoding = self._default_n_hot_encoding.copy()
        categorical_value = self.get_categorical_encoding_value(len(category_list), is_query)
        if is_query:
            n_hot_encoding.fill(constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE)
        category_indices = self._get_category_indices(category_list)
        if category_indices:
            n_hot_encoding[category_indices] = categorical_value
        return n_hot_encoding

    def _get_category_indices(self, text_input: Sequence[str]) -> list[int]:
        return list(
            {
                category_index
                for category_value in text_input
                if (category_index := self._get_index_for_category(category_value)) is not None
            }
        )

    def _get_index_for_category(self, category: str) -> int | None:
        return self._category_index_map.get(
            category, self._other_category_index if self._config.uncategorized_as_category else None
        )

    def _reallocate_vector_values(self, vector: Vector, scaling_factors: Mapping[int, float]) -> Vector:
        if scaling_factors:
            new_values = np.copy(vector.value)
            indices = np.array(list(scaling_factors.keys()), dtype=np.int64)
            factors = np.array(list(scaling_factors.values()), dtype=np.float64)
            new_values[indices] = new_values[indices] * factors
            new_vector = Vector(new_values, vector.negative_filter_indices)
            sum_values = sum(CollectionUtil.get_positive_values_ndarray(new_vector.value))
            normalizing_factor = sum_values / math.sqrt(len(self._config.categories))
            return new_vector.normalize(normalizing_factor)
        return vector

    @override
    async def _to_query_vector(self, input_: Vector, context: ExecutionContext) -> Vector:
        category_vector_values: dict[int, float] = self._get_scaling_factors_for_vector(input_)
        raw_vector: Vector = await self.embed(self.inverse_embed(input_, context), context)
        reallocated_vector: Vector = self._reallocate_vector_values(raw_vector, category_vector_values)
        return reallocated_vector

    def _get_scaling_factors_for_vector(self, vector: Vector) -> dict[int, float]:
        vector_value: NPArray = vector.value
        return dict(zip(vector.non_negative_filter_indices, vector_value[list(vector.non_negative_filter_indices)]))

    @property
    @override
    def needs_inversion_before_aggregation(self) -> bool:
        return False

    @property
    @override
    def length(self) -> int:
        return self._config.length
