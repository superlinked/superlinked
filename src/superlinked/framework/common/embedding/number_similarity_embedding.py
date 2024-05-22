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
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization


class NumberSimilarityEmbedding(Embedding[float], HasLength):
    def __init__(
        self,
        min_value: float,
        max_value: float,
        negative_filter: float,
        normalization: Normalization,
    ) -> None:
        self.__length = 3
        self.__circle_size_in_rad = math.pi / 2
        self._min_value = min_value
        self._max_value = max_value
        self._negative_filter = negative_filter
        self._normalization = normalization

    @override
    def embed(self, input_: float, context: ExecutionContext) -> Vector:
        if input_ < self._min_value or input_ > self._max_value:
            return Vector([0.0, 0.0, self._negative_filter])

        constrained_input: float = min(max(self._min_value, input_), self._max_value)
        normalized_input = (constrained_input - self._min_value) / (
            self._max_value - self._min_value
        )
        angle_in_radians = normalized_input * self.__circle_size_in_rad
        vector_input = np.array(
            [
                math.sin(angle_in_radians),
                math.cos(angle_in_radians),
            ]
        )
        vector = Vector(vector_input).normalize(self._normalization.norm(vector_input))
        vector = vector.concatenate(
            Vector([1.0 if context.is_query_context() else 0.0])
        )
        return vector

    @property
    def length(self) -> int:
        return self.__length
