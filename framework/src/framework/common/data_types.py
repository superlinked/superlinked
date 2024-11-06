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

import numpy as np
from beartype.typing import Any, Mapping, Sequence

from superlinked.framework.common.exception import (
    MismatchingDimensionException,
    NegativeFilterException,
)
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData

Json = Mapping[str, Any]
NPArray = np.ndarray[
    Any,
    np.dtype[np.float64],  # type: ignore # numpy stub is missing for mypy-pylance
]
NP_PRINT_PRECISION = 6


class Vector:
    EMPTY_VECTOR: Vector | None = None

    def __init__(
        self,
        value: Sequence[float] | Sequence[np.float64] | NPArray,
        negative_filter_indices: set[int] | frozenset[int] | None = None,
        vector_before_normalization: Vector | None = None,
    ) -> None:
        if isinstance(value, np.ndarray):
            value_to_set = value
        else:
            value_to_set = np.array(list(value), dtype=np.float64)
        self.value: NPArray = value_to_set
        self.__dimension: int = len(self.value)
        self.__negative_filter_indices = (
            frozenset(negative_filter_indices)
            if negative_filter_indices
            else frozenset({})
        )
        self.__validate_negative_filter_indices()
        self.__vector_before_normalization = vector_before_normalization

    @property
    def dimension(self) -> int:
        return self.__dimension

    @property
    def vector_before_normalization(self) -> Vector | None:
        return self.__vector_before_normalization

    @staticmethod
    def empty_vector() -> Vector:
        if Vector.EMPTY_VECTOR is None:
            Vector.EMPTY_VECTOR = Vector([])
        return Vector.EMPTY_VECTOR

    @property
    def negative_filter_indices(self) -> frozenset[int]:
        return self.__negative_filter_indices

    @property
    def is_empty(self) -> bool:
        return self == Vector.EMPTY_VECTOR

    @property
    def without_negative_filter(self) -> Vector:
        return Vector(self.value[self.non_negative_filter_mask])

    @property
    def non_negative_filter_mask(self) -> np.ndarray:
        mask = np.ones(self.dimension, dtype=np.bool_)
        mask[list(self.negative_filter_indices)] = False
        return mask

    def normalize(self, length: float) -> Vector:
        if length in [0, 1]:
            return self.copy_with_new(vector_before_normalization=self)
        if self.is_empty:
            return self
        normalized = (
            self.copy_with_new(
                self.without_negative_filter.value,
                set(),
                self,
            )
            / length
        )
        return normalized.apply_negative_filter(self)

    def aggregate(self, vector: Vector) -> Vector:
        if self.is_empty:
            return vector.__copy()
        if vector.is_empty:
            return self.__copy()
        if self.dimension != vector.dimension:
            raise MismatchingDimensionException(
                f"Cannot aggregate vectors with different dimensions: {self.dimension} != {vector.dimension}"
            )
        return self.copy_with_new(self.value + vector.value)

    def __validate_negative_filter_indices(self) -> None:
        if not self.negative_filter_indices:
            return
        if len(self.negative_filter_indices) > self.dimension:
            raise NegativeFilterException(
                f"Invalid number of negative filter indices: {len(self.negative_filter_indices)}."
            )
        index_min = min(self.negative_filter_indices)
        if index_min < 0:
            raise NegativeFilterException(
                f"Invalid negative filter index: {index_min}."
            )
        index_max = max(self.negative_filter_indices)
        if index_max > self.dimension - 1:
            raise NegativeFilterException(
                f"Invalid negative filter index: {index_max}."
            )

    def apply_negative_filter(self, other: Vector) -> Vector:
        if self.negative_filter_indices == other.negative_filter_indices:
            values = [
                (self.value[i] if i not in other.negative_filter_indices else value)
                for i, value in enumerate(other.value)
            ]
        else:
            value_iterator = iter(self.value)
            values = [
                (
                    next(value_iterator)
                    if i not in other.negative_filter_indices
                    else value
                )
                for i, value in enumerate(other.value)
            ]
        return self.copy_with_new(values, other.negative_filter_indices)

    def replace_negative_filters(self, new_negative_filter_value: float) -> Vector:
        return self.copy_with_new(
            [
                (
                    new_negative_filter_value
                    if i in self.negative_filter_indices
                    else original_value
                )
                for i, original_value in enumerate(self.value)
            ]
        )

    def concatenate(self, other: Any) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        if self.is_empty:
            return other.__copy()
        if other.is_empty:
            return self.__copy()
        negative_filter_indices = self.negative_filter_indices.union(
            {i + self.dimension for i in other.negative_filter_indices}
        )
        vector_before_normalization = (
            self.vector_before_normalization.concatenate(
                other.vector_before_normalization
            )
            if self.vector_before_normalization and other.vector_before_normalization
            else None
        )
        return self.copy_with_new(
            np.concatenate((self.value, np.array(other.value, dtype=np.float64))),
            negative_filter_indices,
            vector_before_normalization,
        )

    def split(self, lengths: list[int]) -> list[Vector]:
        if sum(lengths) < self.dimension:
            raise ValueError(
                f"The sum of the provided lengths {sum(lengths)} is smaller than the vector dimension {self.dimension}."
            )
        indices = list(np.cumsum(np.array([0] + lengths))[1:].tolist())
        split_values = np.split(self.value, indices)
        split_vectors = []
        for i, length in enumerate(lengths):
            start_index = indices[i - 1] if i > 0 else 0
            end_index = start_index + length
            negative_filter_indices = {
                idx - start_index
                for idx in self.negative_filter_indices
                if start_index <= idx < end_index
            }
            split_vectors.append(Vector(split_values[i], negative_filter_indices, None))
        return split_vectors

    def __mul__(self, other: float | int | Vector) -> Vector:
        if self.is_empty:
            return self
        if isinstance(other, int | float):
            return (
                self.copy_with_new(self.value)
                if float(other) == 1.0
                else self.copy_with_new(self.value * float(other))
            )
        if self.dimension != other.dimension:
            raise ValueError(
                f"Vector dimensions are not equal. First Vector dimension={self.dimension} "
                f"other Vector dimension={other.dimension}"
            )
        return self.copy_with_new(self.value * other.value)

    def __truediv__(self, other: Any) -> Vector:
        if (not isinstance(other, (float, int))) or other == 0:
            return NotImplemented
        if self.is_empty:
            return self
        return self.copy_with_new(self.value / float(other))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector):
            return (
                np.array_equal(self.value, other.value)
                and self.negative_filter_indices == other.negative_filter_indices
            )
        return False

    def __hash__(self) -> int:
        return hash((str(self.value), self.negative_filter_indices))

    def copy_with_new(
        self,
        value: list[float] | list[np.float64] | NPArray | None = None,
        negative_filter_indices: set[int] | frozenset[int] | None = None,
        vector_before_normalization: Vector | None = None,
    ) -> Vector:
        value_to_use = self.value if value is None else value
        vector_before_normalization_to_use = (
            (
                self.vector_before_normalization.copy_with_new()
                if self.vector_before_normalization is not None
                else None
            )
            if vector_before_normalization is None
            else vector_before_normalization.copy_with_new()
        )
        negative_filter_indices_to_use = (
            self.negative_filter_indices
            if negative_filter_indices is None
            else negative_filter_indices
        )
        return Vector(
            value_to_use.copy(),
            negative_filter_indices_to_use.copy(),
            vector_before_normalization_to_use,
        )

    def __copy(self) -> Vector:
        if self.is_empty:
            return self
        return self.copy_with_new()

    def __str__(self) -> str:
        return np.array_str(  # type: ignore # numpy stub is missing for mypy-pylance
            self.value, precision=NP_PRINT_PRECISION, suppress_small=True
        )

    @classmethod
    def init_zero_vector(cls, length: int) -> Vector:
        return Vector([0] * length)


PythonTypes = float | int | str | Vector | list[float] | list[str] | BlobInformation
NodeDataTypes = PythonTypes | ImageData
