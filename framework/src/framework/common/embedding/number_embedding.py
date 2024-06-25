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
from enum import Enum

import numpy as np
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.interface.has_default_vector import HasDefaultVector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization


class Mode(Enum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    SIMILAR = "similar"


class NumberEmbedding(
    Embedding[float], HasLength, HasDefaultVector
):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        min_value: float,
        max_value: float,
        mode: Mode,
        negative_filter: float,
        normalization: Normalization,
    ) -> None:
        self.__circle_size_in_rad = math.pi / 2
        self.__length = 3
        self._min_value = min_value
        self._max_value = max_value
        self._mode = mode
        self._negative_filter = negative_filter
        self._normalization = normalization
        self.__default_vector = {
            Mode.SIMILAR: [0.0, 0.0, 0.0],
            Mode.MINIMUM: [0.0, 1.0, 1.0],
            Mode.MAXIMUM: [1.0, 0.0, 1.0],
        }[self._mode]

    @property
    @override
    def default_vector(self) -> Vector:
        return Vector(self.__default_vector)

    def should_return_default(self, context: ExecutionContext) -> bool:
        return context.should_load_default_node_input or (
            context.is_query_context
            and self._mode
            in {
                Mode.MINIMUM,
                Mode.MAXIMUM,
            }
        )

    @override
    def embed(
        self,
        input_: float,
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> Vector:
        if (
            input_ < self._min_value
            and self._mode
            in {
                Mode.MAXIMUM,
                Mode.SIMILAR,
            }
        ) or (
            input_ > self._max_value
            and self._mode
            in {
                Mode.MINIMUM,
                Mode.SIMILAR,
            }
        ):
            return Vector(list(self._value_when_out_of_bounds), {2})
        constrained_input: float = min(max(self._min_value, input_), self._max_value)
        normalized_input = (constrained_input - self._min_value) / (
            self._max_value - self._min_value
        )
        angle_in_radians = normalized_input * self.__circle_size_in_rad
        vector_input = np.array(
            [math.sin(angle_in_radians), math.cos(angle_in_radians)]
        )
        vector = Vector(np.append(vector_input, [0.0]), {2}).normalize(
            self._normalization.norm(vector_input)
        )
        return vector

    @override
    def inverse_embed(
        self,
        vector: Vector,
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> float:
        """
        This function might seem complex,
        but it essentially performs the inverse operation of the embed function.
        """
        denormalized = self._normalization.denormalize(vector)
        if list(vector.value) == self._value_when_out_of_bounds:
            if self._mode == Mode.MAXIMUM:
                return self._min_value - 1
            # INFO: for similar it doesn't matter, which direction is it out of bounds
            return self._max_value + 1

        angle_in_radians = math.atan2(denormalized.value[0], denormalized.value[1])
        transformed_number = angle_in_radians / self.__circle_size_in_rad
        transformed_number = (
            transformed_number * (self._max_value - self._min_value) + self._min_value
        )
        return transformed_number

    @property
    def _value_when_out_of_bounds(self) -> Sequence[float]:
        return [0.0, 0.0, self._negative_filter]

    @property
    def length(self) -> int:
        return self.__length
