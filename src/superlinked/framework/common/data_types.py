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

from collections.abc import Mapping
from typing import Any, Union

import numpy as np
import numpy.typing as npt

# For some reason mypy does not recognize this import
from numpy.linalg import norm  # type: ignore[attr-defined]

from superlinked.framework.common.exception import MismatchingDimensionException

Json = Mapping[str, Any]


class Vector:
    EMPTY_VECTOR: Vector | None = None

    def __init__(self, value: Union[list[float], npt.NDArray[np.float64]]) -> None:
        if isinstance(value, np.ndarray):
            value_to_set = value
        else:
            value_to_set = np.array(value, dtype=float)
        self.value: npt.NDArray[np.float64] = value_to_set
        self.__length: float = norm(self.value)
        self.__dimension: int = len(self.value)

    @property
    def length(self) -> float:
        return self.__length

    @property
    def dimension(self) -> int:
        return self.__dimension

    @staticmethod
    def empty_vector() -> Vector:
        if Vector.EMPTY_VECTOR is None:
            Vector.EMPTY_VECTOR = Vector([])
        return Vector.EMPTY_VECTOR

    @property
    def is_empty(self) -> bool:
        return self == Vector.EMPTY_VECTOR

    def normalize(self) -> Vector:
        if self.is_empty:
            return self
        return self / (self.length if self.length != 0 else 1)

    def aggregate(self, vector: Vector) -> Vector:
        if self.is_empty:
            return vector.__copy()
        if vector.is_empty:
            return self.__copy()
        if self.dimension != vector.dimension:
            raise MismatchingDimensionException(
                f"Cannot aggregate vectors with different dimensions: {self.dimension} != {vector.dimension}"
            )
        return Vector(self.value + vector.value)

    def __add__(self, other: Any) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        if self.is_empty:
            return other.__copy()
        if other.is_empty:
            return self.__copy()
        return Vector(np.concatenate((self.value, np.array(other.value, dtype=float))))

    def __mul__(self, other: float | int | Vector) -> Vector:
        if self.is_empty:
            return self

        if isinstance(other, Vector):
            if self.dimension != other.dimension:
                raise ValueError(
                    f"Vector dimensions are not equal. First Vector dimension={self.dimension} "
                    f"other Vector dimension={other.dimension}"
                )
            return Vector(np.multiply(self.value, other.value))
        if isinstance(other, int | float):
            return (
                Vector(self.value)
                if float(other) == 1.0
                else Vector(self.value * float(other))
            )
        raise NotImplementedError(
            f"Vector multiplication is only implemented for Vector and int | float types."
            f"Got {type(other)}"
        )

    def __truediv__(self, other: Any) -> Vector:
        if (not isinstance(other, (float, int))) or other == 0:
            return NotImplemented
        if self.is_empty:
            return self
        return Vector(self.value / float(other))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector):
            return np.array_equal(self.value, other.value)
        return False

    def __copy(self) -> Vector:
        if self.is_empty:
            return self
        return Vector(self.value.copy())
