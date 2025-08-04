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

from beartype.typing import Sequence, cast
from cachetools import LRUCache

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidStateException


class TextEmbeddingCache:
    def __init__(self, cache_size: int) -> None:
        self._cache_size = cache_size
        self._cache: LRUCache = LRUCache(self._cache_size)

    def calculate_cache_info(self, inputs: Sequence[str]) -> tuple[list[str], list[int], list[Vector]]:
        if self._cache_size == 0:
            return list(inputs), [], []

        inputs_to_embed = []
        found_indices = []
        existing_vectors = []

        for i, input_ in enumerate(inputs):
            vector = self._cache.get(input_)
            if vector is None:
                inputs_to_embed.append(input_)
            else:
                existing_vectors.append(vector)
                found_indices.append(i)

        return inputs_to_embed, found_indices, existing_vectors

    def update(self, inputs_to_embed: Sequence[str], uncached_vectors: Sequence[Vector]) -> None:
        if self._cache_size == 0 or not inputs_to_embed:
            return
        if len(inputs_to_embed) != len(uncached_vectors):
            raise InvalidStateException(
                "Number of inputs must match number of vectors.",
                num_inputs=len(inputs_to_embed),
                num_vectors=len(uncached_vectors),
            )
        for input_, vector in zip(inputs_to_embed, uncached_vectors):
            self._cache[input_] = vector

    def combine_vectors(
        self,
        inputs_to_embed: list[str],
        found_indices: list[int],
        existing_vectors: list[Vector],
        uncached_vectors: Sequence[Vector],
    ) -> Sequence[Vector]:
        total_size = len(existing_vectors) + len(inputs_to_embed)
        result: list[Vector | None] = [None] * total_size

        for pos, vector in zip(found_indices, existing_vectors):
            result[pos] = vector

        uncached_idx = 0
        for i in range(total_size):
            if result[i] is None:
                result[i] = uncached_vectors[uncached_idx]
                uncached_idx += 1

        return cast(list[Vector], result)
