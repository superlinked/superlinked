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

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength


class Mode(Enum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    SIMILAR = "similar"


class NumberEmbedding(HasLength):
    def __init__(
        self,
        min_value: float,
        max_value: float,
        mode: Mode,
        negative_filter: float,
    ) -> None:
        self.__length = 1
        self.min_value = min_value
        self.max_value = max_value
        self.mode = mode
        self.negative_filter = float(negative_filter)

    def transform(self, input_number: float) -> Vector:
        constrained_input: float = min(
            max(self.min_value, input_number), self.max_value
        )
        transformed_number: float = (constrained_input - self.min_value) / (
            self.max_value - self.min_value
        )
        if self.mode == Mode.MINIMUM:
            transformed_number = 1 - transformed_number
        if transformed_number <= 0:
            transformed_number = self.negative_filter

        return Vector(np.array([transformed_number]).astype(np.float32).tolist())

    @property
    def length(self) -> int:
        return self.__length
