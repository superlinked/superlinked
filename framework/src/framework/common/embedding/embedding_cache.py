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
from cachetools import LRUCache

from superlinked.framework.common.data_types import Vector


@dataclass(frozen=True)
class CacheInformation:
    inputs_to_embed: Sequence[str]
    found_indices: Sequence[int]
    existing_vectors: Sequence[Vector]

    def combine_vectors(self, uncached_vectors: list[Vector]) -> list[Vector]:
        vectors: list[Vector] = []
        existing_index = 0
        new_index = 0
        item_count = len(self.existing_vectors) + len(self.inputs_to_embed)
        for i in range(item_count):
            if (
                existing_index < len(self.found_indices)
                and self.found_indices[existing_index] == i
            ):
                vectors.append(self.existing_vectors[existing_index])
                existing_index += 1
            else:
                vectors.append(uncached_vectors[new_index])
                new_index += 1
        return vectors


class EmbeddingCache:
    def __init__(self, cache_size: int) -> None:
        self._cache_size = cache_size
        self._cache: LRUCache = LRUCache(self._cache_size)

    def calculate_cache_info(self, inputs: Sequence[str]) -> CacheInformation:
        if self._cache_size == 0:
            return CacheInformation(inputs, [], [])

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
        return CacheInformation(inputs_to_embed, found_indices, existing_vectors)

    def update(
        self, inputs_to_embed: Sequence[str], uncached_vectors: Sequence[Vector]
    ) -> None:
        if self._cache_size == 0:
            return
        if not inputs_to_embed:
            return
        for input_, vector in zip(inputs_to_embed, uncached_vectors):
            self._cache[input_] = vector
