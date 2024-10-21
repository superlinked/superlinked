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
from beartype.typing import cast
from typing_extensions import TypeVar, override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.number_embedding_config import (
    LogarithmicScale,
    Mode,
    NumberEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.embedding import InvertibleEmbedding

NumberT = TypeVar("NumberT", int, float)


class NumberEmbedding(InvertibleEmbedding[NumberT, NumberEmbeddingConfig]):
    def __init__(self, embedding_config: NumberEmbeddingConfig) -> None:
        super().__init__(embedding_config)
        self._default_vector = self._config.default_vector
        self._circle_size_in_rad = math.pi / 2
        self._value_when_out_of_bounds = [0.0, 0.0, self._config.negative_filter]

    @property
    @override
    def default_vector(self) -> Vector:
        return self._default_vector

    @property
    @override
    def length(self) -> int:
        return self._config.length

    @override
    def embed(self, input_: float, context: ExecutionContext) -> Vector:
        if (
            input_ < self._config.min_value
            and self._config.mode
            in {
                Mode.MAXIMUM,
                Mode.SIMILAR,
            }
        ) or (
            input_ > self._config.max_value
            and self._config.mode
            in {
                Mode.MINIMUM,
                Mode.SIMILAR,
            }
        ):
            return Vector(list(self._value_when_out_of_bounds), {2})
        transformed_input = self._transform_to_log_if_logarithmic(input_)
        transformed_min = self._transform_to_log_if_logarithmic(self._config.min_value)
        transformed_max = self._transform_to_log_if_logarithmic(self._config.max_value)
        constrained_input: float = min(
            max(transformed_min, transformed_input), transformed_max
        )
        normalized_input = (constrained_input - transformed_min) / (
            transformed_max - transformed_min
        )
        angle_in_radians = normalized_input * self._circle_size_in_rad
        vector_input = np.array(
            [math.sin(angle_in_radians), math.cos(angle_in_radians)]
        )
        return Vector(np.append(vector_input, [0.0]), {2})

    @override
    def inverse_embed(self, vector: Vector, context: ExecutionContext) -> NumberT:
        """
        This function might seem complex,
        but it essentially performs the inverse operation of the embed function.
        """
        if len(vector.value) != self.length:
            raise ValueError(
                f"Mismatching length {len(vector.value)} of the vector to inverse embed"
            )
        if list(vector.value) == self._value_when_out_of_bounds:
            out_of_bounds_bias: float = (
                self._config.max_value - self._config.min_value
            ) / 1000.0
            if self._config.mode == Mode.MAXIMUM:
                return cast(NumberT, self._config.min_value - out_of_bounds_bias)
            # INFO: for similar it doesn't matter, which direction is it out of bounds
            return cast(NumberT, self._config.max_value + out_of_bounds_bias)
        angle_in_radians = math.atan2(vector.value[0], vector.value[1])
        transformed_number = angle_in_radians / self._circle_size_in_rad
        transformed_max = self._transform_to_log_if_logarithmic(self._config.max_value)
        transformed_min = self._transform_to_log_if_logarithmic(self._config.min_value)
        transformed_input_ = (
            transformed_number * (transformed_max - transformed_min) + transformed_min
        )
        input_ = self._transform_from_log_if_logarithmic(transformed_input_)
        return cast(NumberT, input_)

    @property
    @override
    def needs_inversion_before_aggregation(self) -> bool:
        return True

    def _transform_to_log_if_logarithmic(self, value: float) -> float:
        return (
            math.log(1 + value, self._config.scale.base)
            if isinstance(self._config.scale, LogarithmicScale)
            else value
        )

    def _transform_from_log_if_logarithmic(self, value: float) -> float:
        return round(
            (
                self._config.scale.base**value - 1
                if isinstance(self._config.scale, LogarithmicScale)
                else value
            ),
            10,
        )
