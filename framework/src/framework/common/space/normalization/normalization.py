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

from abc import ABC, abstractmethod

from beartype.typing import Any, Generic, Sequence, TypeVar
from scipy import linalg
from typing_extensions import override

from superlinked.framework.common.data_types import NPArray, Vector
from superlinked.framework.common.space.config.normalization.normalization_config import (
    ConstantNormConfig,
    L2NormConfig,
    NoNormConfig,
    NormalizationConfig,
)

NormalizationConfigT = TypeVar("NormalizationConfigT", bound=NormalizationConfig)


class Normalization(Generic[NormalizationConfigT], ABC):
    def __init__(self, config: NormalizationConfigT) -> None:
        self._config = config

    def normalize(self, vector: Vector) -> Vector:
        return vector.normalize(self.norm(vector.without_negative_filter.value))

    def normalize_multiple(self, vectors: Sequence[Vector]) -> list[Vector]:
        return [self.normalize(vector) for vector in vectors]

    @abstractmethod
    def norm(self, value: NPArray) -> float: ...

    def denormalize(self, vector: Vector) -> Vector:
        if vector.vector_before_normalization is None:
            return vector
        return vector.vector_before_normalization.apply_negative_filter(vector)

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


class L2Norm(Normalization[L2NormConfig]):
    def __init__(self, config: L2NormConfig | None = None) -> None:
        super().__init__(config or L2NormConfig())

    @override
    def norm(self, value: NPArray) -> float:
        """Must be called with value that has no negative filter"""
        return linalg.norm(value)


class ConstantNorm(Normalization[ConstantNormConfig]):
    def __init__(self, config: ConstantNormConfig) -> None:
        super().__init__(config)
        self.__validate_length()

    def __validate_length(self) -> None:
        if self._config.length == 0:
            raise ValueError("Normalization length cannot be zero.")

    @override
    def norm(self, value: NPArray) -> float:
        return self._config.length

    @override
    def denormalize(self, vector: Vector) -> Vector:
        return vector.normalize(1 / self._config.length)

    @override
    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, type(self))
            and self._config.length == other._config.length
        )


class NoNorm(Normalization[NoNormConfig]):
    def __init__(self, config: NoNormConfig | None = None) -> None:
        super().__init__(config or NoNormConfig())

    @override
    def norm(self, value: NPArray) -> float:
        return 1.0
