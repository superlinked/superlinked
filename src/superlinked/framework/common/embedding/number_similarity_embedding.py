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

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength


class NumberSimilarityEmbedding(HasLength):
    def __init__(
        self, min_value: float, max_value: float, negative_filter: float
    ) -> None:
        self.__length = 3
        self.__circle_size_in_rad = math.pi / 2
        self.min_value = min_value
        self.max_value = max_value
        self.negative_filter = negative_filter

    def transform(self, input_number: float, is_query: bool) -> Vector:
        if input_number < self.min_value or input_number > self.max_value:
            return Vector([0.0, 0.0, self.negative_filter])

        constrained_input: float = min(
            max(self.min_value, input_number), self.max_value
        )
        normalized_input = (constrained_input - self.min_value) / (
            self.max_value - self.min_value
        )
        angle_in_radians = normalized_input * self.__circle_size_in_rad
        return Vector(
            [
                math.sin(angle_in_radians),
                math.cos(angle_in_radians),
                1.0 if is_query else 0.0,
            ]
        )

    @property
    def length(self) -> int:
        return self.__length
