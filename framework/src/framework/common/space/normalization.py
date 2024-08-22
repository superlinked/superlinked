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

from beartype.typing import Any
from scipy import linalg
from typing_extensions import override

from superlinked.framework.common.data_types import NPArray, Vector


class Normalization(ABC):

    def normalize(self, vector: Vector) -> Vector:
        return vector.normalize(self.norm(vector.without_negative_filter.value))

    @abstractmethod
    def norm(self, value: NPArray) -> float: ...

    def denormalize(self, vector: Vector) -> Vector:
        if vector.vector_before_normalization is None:
            return vector
        return vector.vector_before_normalization.apply_negative_filter(vector)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__ if self.__dict__ else ''})"


class L2Norm(Normalization):
    @override
    def norm(self, value: NPArray) -> float:
        """Must be called with value that has no negative filter"""
        return linalg.norm(value)

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
    def norm(self, value: NPArray) -> float:
        return self.length

    @override
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self.length == other.length


class NoNorm(ConstantNorm):
    def __init__(self) -> None:
        super().__init__(1)
