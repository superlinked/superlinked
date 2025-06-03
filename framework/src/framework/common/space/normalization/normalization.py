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

from __future__ import annotations

import math
from abc import ABC, abstractmethod

import numpy as np
from beartype.typing import Any, Generic, Sequence, TypeVar
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import NPArray, Vector
from superlinked.framework.common.space.config.normalization.normalization_config import (
    CategoricalNormConfig,
    ConstantNormConfig,
    L1NormConfig,
    L2NormConfig,
    NoNormConfig,
    NormalizationConfig,
)
from superlinked.framework.common.util.collection_util import CollectionUtil

NormalizationConfigT = TypeVar("NormalizationConfigT", bound=NormalizationConfig)


class Normalization(Generic[NormalizationConfigT], ABC):
    def __init__(self, config: NormalizationConfigT) -> None:
        self._config = config

    def normalize(self, vector: Vector, context: ExecutionContext | None = None) -> Vector:
        return vector.normalize(
            self.norm(
                vector.value_without_negative_filter,
                context.is_query_context if context is not None else False,
            )
        )

    def normalize_multiple(self, vectors: Sequence[Vector], context: ExecutionContext) -> list[Vector]:
        return [self.normalize(vector, context) for vector in vectors]

    @abstractmethod
    def norm(self, value: NPArray, is_query: bool = False) -> float: ...

    def denormalize(self, vector: Vector) -> Vector:
        return vector.denormalize()

    def denormalize_multiple(self, vectors: Sequence[Vector]) -> list[Vector]:
        return [self.denormalize(vector) for vector in vectors]

    @override
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self._config == other._config

    @override
    def __hash__(self) -> int:
        return hash(self._config)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__ if self.__dict__ else ''})"


class L1Norm(Normalization[L1NormConfig]):
    def __init__(self, config: L1NormConfig | None = None) -> None:
        super().__init__(config or L1NormConfig())

    @override
    def norm(self, value: NPArray, is_query: bool = False) -> float:
        """Returns the L1 norm (sum of absolute values) of the input array"""
        return np.sum(np.abs(value))


class L2Norm(Normalization[L2NormConfig]):
    def __init__(self, config: L2NormConfig | None = None) -> None:
        super().__init__(config or L2NormConfig())

    @override
    def norm(self, value: NPArray, is_query: bool = False) -> float:
        """Must be called with value that has no negative filter"""
        return np.linalg.norm(value)  # type: ignore[attr-defined]  # np cannot find norm


class ConstantNorm(Normalization[ConstantNormConfig]):
    def __init__(self, config: ConstantNormConfig) -> None:
        super().__init__(config)
        self.__validate_length()

    def __validate_length(self) -> None:
        if self._config.length == 0:
            raise ValueError("Normalization length cannot be zero.")

    @override
    def norm(self, value: NPArray, is_query: bool = False) -> float:
        return self._config.length

    @override
    def denormalize(self, vector: Vector) -> Vector:
        return vector.normalize(1 / self._config.length)

    @override
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self._config.length == other._config.length


class NoNorm(Normalization[NoNormConfig]):
    def __init__(self, config: NoNormConfig | None = None) -> None:
        super().__init__(config or NoNormConfig())

    @override
    def norm(self, value: NPArray, is_query: bool = False) -> float:
        return 1.0


class CategoricalNorm(Normalization[CategoricalNormConfig]):
    def __init__(self, config: CategoricalNormConfig) -> None:
        super().__init__(config)

    @override
    def norm(self, value: NPArray, is_query: bool = False) -> float:
        vector_values_max: float = float(np.max(value, initial=0.0))  # type: ignore[call-overload] # it exists
        len_implied_categories: int = len(CollectionUtil.get_positive_values_ndarray(value))
        sqrt_len_config_categories: float = math.sqrt(self._config.categories_count)
        expected_max: float = (
            sqrt_len_config_categories / (len_implied_categories or 1.0)
            if is_query
            else 1.0 / sqrt_len_config_categories
        )
        return vector_values_max / expected_max
