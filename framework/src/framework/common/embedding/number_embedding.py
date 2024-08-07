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
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Scale:
    pass


@dataclass(frozen=True)
class LinearScale(Scale):
    pass


@dataclass(frozen=True)
class LogarithmicScale(Scale):
    base: float = 10

    def __post_init__(self) -> None:
        if self.base <= 1:
            raise ValueError("Logarithmic function base must larger than 1.")


class NumberEmbedding(
    Embedding[float], HasLength, HasDefaultVector
):  # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(
        self,
        min_value: float,
        max_value: float,
        mode: Mode,
        scale: Scale,
        negative_filter: float,
        normalization: Normalization,
    ) -> None:
        if isinstance(scale, LogarithmicScale) and min_value < 0:
            raise ValueError(
                "Min value must be 0 or higher when using logarithmic scale."
            )
        if isinstance(scale, LogarithmicScale) and max_value < 0:
            raise ValueError("Max value cannot be 0 when using logarithmic scale.")
        self.__circle_size_in_rad = math.pi / 2
        self.__length = 3
        self._min_value = min_value
        self._max_value = max_value
        self._mode = mode
        self._scale = scale
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
        transformed_input = self._transform_to_log_if_logarithmic(input_)
        transformed_min = self._transform_to_log_if_logarithmic(self._min_value)
        transformed_max = self._transform_to_log_if_logarithmic(self._max_value)
        constrained_input: float = min(
            max(transformed_min, transformed_input), transformed_max
        )
        normalized_input = (constrained_input - transformed_min) / (
            transformed_max - transformed_min
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
            out_of_bounds_bias = (self._max_value - self._min_value) / 1000
            if self._mode == Mode.MAXIMUM:
                return self._min_value - out_of_bounds_bias
            # INFO: for similar it doesn't matter, which direction is it out of bounds
            return self._max_value + out_of_bounds_bias
        angle_in_radians = math.atan2(denormalized.value[0], denormalized.value[1])
        transformed_number = angle_in_radians / self.__circle_size_in_rad
        transformed_max = self._transform_to_log_if_logarithmic(self._max_value)
        transformed_min = self._transform_to_log_if_logarithmic(self._min_value)
        transformed_input_ = (
            transformed_number * (transformed_max - transformed_min) + transformed_min
        )
        input_ = self._transform_from_log_if_logarithmic(transformed_input_)
        return input_

    def _transform_to_log_if_logarithmic(self, value: float) -> float:
        return (
            math.log(1 + value, self._scale.base)
            if isinstance(self._scale, LogarithmicScale)
            else value
        )

    def _transform_from_log_if_logarithmic(self, value: float) -> float:
        return round(
            (
                self._scale.base**value - 1
                if isinstance(self._scale, LogarithmicScale)
                else value
            ),
            10,
        )

    @property
    def _value_when_out_of_bounds(self) -> Sequence[float]:
        return [0.0, 0.0, self._negative_filter]

    @property
    def length(self) -> int:
        return self.__length
