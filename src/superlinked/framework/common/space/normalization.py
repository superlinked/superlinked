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

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import numpy.typing as npt
from typing_extensions import override

from superlinked.framework.common.data_types import Vector


class Normalization(ABC):

    @abstractmethod
    def norm(self, value: npt.NDArray[np.float64]) -> float: ...

    def denormalize(self, vector: Vector) -> Vector:
        if vector.vector_before_normalization is None:
            return vector
        return vector.vector_before_normalization.apply_negative_filter(vector)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__ if self.__dict__ else ''})"


class L2Norm(Normalization):
    @override
    def norm(self, value: npt.NDArray[np.float64]) -> float:
        return np.linalg.norm(value)  # type: ignore[attr-defined]

    @override
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self))


class ConstantNorm(Normalization):
    def __init__(self, length: float) -> None:
        self.length = length
        self.__validate_length()

    def __validate_length(self) -> None:
        if self.length == 0:
            raise ValueError("Normalization length cannot be zero.")

    @override
    def norm(self, value: npt.NDArray[np.float64]) -> float:
        return self.length

    @override
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self.length == other.length


class NoNorm(ConstantNorm):
    def __init__(self) -> None:
        super().__init__(1)
