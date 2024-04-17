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

from enum import Enum

import numpy as np
from typing_extensions import override

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization


class Mode(Enum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    SIMILAR = "similar"


class NumberEmbedding(Embedding[float], HasLength):
    def __init__(
        self,
        min_value: float,
        max_value: float,
        mode: Mode,
        negative_filter: float,
        normalization: Normalization,
    ) -> None:
        self.__length = 1
        self.min_value = min_value
        self.max_value = max_value
        self.mode = mode
        self.negative_filter = float(negative_filter)
        self.__normalization = normalization

    @override
    def embed(
        self,
        input_: float,
        is_query: bool,  # pylint: disable=unused-argument
    ) -> Vector:
        constrained_input: float = min(max(self.min_value, input_), self.max_value)
        transformed_number: float = (constrained_input - self.min_value) / (
            self.max_value - self.min_value
        )
        if self.mode == Mode.MINIMUM:
            transformed_number = 1 - transformed_number
        if transformed_number <= 0:
            transformed_number = self.negative_filter
        vector_input = np.array([transformed_number])
        vector = Vector(vector_input)
        return vector.normalize(self.__normalization.norm(vector_input))

    @property
    def length(self) -> int:
        return self.__length
