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
from typing_extensions import override

from superlinked.framework.common.exception import (
    MismatchingDimensionException,
    NegativeFilterException,
)
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData

Json = Mapping[str, Any]
NPArray = np.ndarray[np.float64]
NP_PRINT_PRECISION = 6


class Vector:

    def __init__(
        self,
        value: Sequence[float] | Sequence[np.float64] | NPArray,
        negative_filter_indices: set[int] | frozenset[int] | None = None,
        denormalizer: float = 1.0,
    ) -> None:
        if isinstance(value, np.ndarray):
            value_to_set = value
        else:
            value_to_set = np.array(list(value), dtype=np.float64)
        self.value: NPArray = value_to_set
        self.__make_value_immutable()
        self.__dimension: int = len(self.value)
        self.__negative_filter_indices = (
            frozenset(negative_filter_indices) if negative_filter_indices else frozenset({})
        )
        self.__validate_negative_filter_indices()
        self.__denormalizer = denormalizer

    def __make_value_immutable(self) -> None:
        self.value.setflags(write=False)

    @property
    def dimension(self) -> int:
        return self.__dimension

    @property
    def denormalizer(self) -> float:
        return self.__denormalizer

    @staticmethod
    def empty_vector() -> Vector:
        return Vector([])

    @property
    def negative_filter_indices(self) -> frozenset[int]:
        return self.__negative_filter_indices

    @property
    def non_negative_filter_indices(self) -> set[int]:
        return set(range(self.dimension)) - set(self.negative_filter_indices)

    @property
    def is_empty(self) -> bool:
        return self.dimension == 0

    @property
    def value_without_negative_filter(self) -> NPArray:
        if self.__negative_filter_indices:
            return self.value[self.non_negative_filter_mask]
        return self.value

    @property
    def non_negative_filter_mask(self) -> np.ndarray:
        mask = np.ones(self.dimension, dtype=np.bool_)
        mask[list(self.negative_filter_indices)] = False
        return mask

    def normalize(self, length: float) -> Vector:
        if length in [0, 1] or self.is_empty:
            return self
        normalized = self.shallow_copy_with_new(self.value_without_negative_filter / float(length), set(), 1 / length)
        return normalized.apply_negative_filter(self)

    def denormalize(self) -> Vector:
        return self.normalize(self.denormalizer)

    def aggregate(self, vector: Vector) -> Vector:
        if self.is_empty:
            return vector
        if vector.is_empty:
            return self
        if self.dimension != vector.dimension:
            raise MismatchingDimensionException(
                f"Cannot aggregate vectors with different dimensions: {self.dimension} != {vector.dimension}"
            )
        return self.shallow_copy_with_new(
            self.value + vector.value,
            negative_filter_indices=self.negative_filter_indices.intersection(vector.negative_filter_indices),
        )

    def __validate_negative_filter_indices(self) -> None:
        if not self.negative_filter_indices:
            return
        if len(self.negative_filter_indices) > self.dimension:
            raise NegativeFilterException(
                f"Invalid number of negative filter indices: {len(self.negative_filter_indices)}."
            )
        index_min = min(self.negative_filter_indices)
        if index_min < 0:
            raise NegativeFilterException(f"Invalid negative filter index: {index_min}.")
        index_max = max(self.negative_filter_indices)
        if index_max > self.dimension - 1:
            raise NegativeFilterException(f"Invalid negative filter index: {index_max}.")

    def apply_negative_filter(self, other: Vector) -> Vector:
        if self.negative_filter_indices == other.negative_filter_indices:
            values = [
                (value if i in other.negative_filter_indices else self.value[i]) for i, value in enumerate(other.value)
            ]
        else:
            value_iterator = iter(self.value)
            values = [
                (value if i in other.negative_filter_indices else next(value_iterator))
                for i, value in enumerate(other.value)
            ]
        return self.shallow_copy_with_new(values, other.negative_filter_indices)

    def replace_negative_filters(self, new_negative_filter_value: float) -> Vector:
        return self.shallow_copy_with_new(
            [
                (new_negative_filter_value if i in self.negative_filter_indices else original_value)
                for i, original_value in enumerate(self.value)
            ]
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
                idx - start_index for idx in self.negative_filter_indices if start_index <= idx < end_index
            }
            split_vectors.append(Vector(split_values[i], negative_filter_indices))
        return split_vectors

    def __mul__(self, other: Any) -> Vector:
        if self.is_empty:
            return self
        if not isinstance(other, int | float):
            raise ValueError(f"{type(self).__name__} can only be multiplied with int or float")
        if other == 1:
            return self
        if other == 0:
            return Vector(np.zeros(self.dimension, dtype=np.float64), self.negative_filter_indices)

        multiplied_vector = Vector(self.value_without_negative_filter * float(other))
        return multiplied_vector.apply_negative_filter(self)

    def __rmul__(self, other: Any) -> Vector:
        return self * other

    def __truediv__(self, other: Any) -> Vector:
        if other == 0:
            return NotImplemented
        return self * (1 / other)

    @override
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector):
            return (
                np.array_equal(self.value, other.value)
                and self.negative_filter_indices == other.negative_filter_indices
            )
        return False

    @override
    def __hash__(self) -> int:
        return hash((str(self.value), self.negative_filter_indices))

    def shallow_copy_with_new(
        self,
        value: list[float] | list[np.float64] | NPArray | None = None,
        negative_filter_indices: set[int] | frozenset[int] | None = None,
        denormalizer: float | None = None,
    ) -> Vector:
        value_to_use = self.value if value is None else value
        negative_filter_indices_to_use = (
            self.negative_filter_indices if negative_filter_indices is None else negative_filter_indices
        )
        denormalizer_to_use = self.denormalizer if denormalizer is None else denormalizer
        return Vector(value_to_use, negative_filter_indices_to_use, denormalizer_to_use)

    def to_list(self) -> list[float]:
        return [float(x) for x in self.value.tolist()]

    def __str__(self) -> str:
        return np.array_str(  # type: ignore # numpy stub is missing for mypy-pylance
            self.value, precision=NP_PRINT_PRECISION, suppress_small=True
        )

    @override
    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def init_zero_vector(cls, length: int) -> Vector:
        return Vector([0] * length)


PythonTypes = float | int | str | Vector | list[float] | list[str] | BlobInformation
NodeDataTypes = PythonTypes | ImageData
