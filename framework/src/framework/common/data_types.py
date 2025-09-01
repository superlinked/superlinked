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

from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData

Json = Mapping[str, Any]
VectorItemT = np.float32
NPArray = np.ndarray[VectorItemT]
NP_PRINT_PRECISION = 6


class Vector:

    def __init__(
        self,
        value: Sequence[float] | Sequence[np.floating] | NPArray,
        negative_filter_indices: set[int] | frozenset[int] | None = None,
        denormalizer: float = 1.0,
    ) -> None:
        self.value = self.__init_value(value)
        self.__negative_filter_indices = self.__init_negative_filter_indices(negative_filter_indices, self.dimension)
        self._denormalizer = denormalizer

    @staticmethod
    def empty_vector() -> Vector:
        return Vector([])

    @staticmethod
    def init_zero_vector(length: int) -> Vector:
        return Vector([0] * length)

    @property
    def dimension(self) -> int:
        return len(self.value)

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
        if not self.__negative_filter_indices:
            return self.value
        return self.value[self.value_mask]

    @property
    def value_mask(self) -> np.ndarray[np.bool_]:
        mask = np.ones(self.dimension, dtype=np.bool_)
        if len(self.__negative_filter_indices):
            mask[list(self.__negative_filter_indices)] = False
        return mask

    def normalize(self, length: float) -> Vector:
        if length == 0:
            return self
        divided_vector = self / length
        return divided_vector.__shallow_copy_with_new(denormalizer=1 / length)

    def denormalize(self) -> Vector:
        return self.normalize(self._denormalizer)

    def split(self, lengths: Sequence[int]) -> list[Vector]:
        if sum(lengths) < self.dimension:
            raise InvalidStateException(
                "The sum of the provided lengths is smaller than the vector dimension.",
                lengths=lengths,
                vector_dimension=self.dimension,
            )
        indices = list(np.cumsum(np.array([0] + list(lengths)))[1:].tolist())
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

    def to_list(self) -> list[float]:
        return list(self.value.astype(float).tolist())

    def __mul__(self, other: Any) -> Vector:
        if other == 0:
            value = np.zeros(
                self.dimension,
                dtype=VectorItemT,  # type: ignore[arg-type] # it is valid
            )
            return Vector(value, self.negative_filter_indices)
        if other == 1 or self.is_empty:
            return self
        if not isinstance(other, int | float | np.floating):
            raise InvalidStateException(
                f"{type(self).__name__} can only be multiplied with int, float or np.floating",
                invalid_type=type(other).__name__,
            )
        value = np.multiply(  # type: ignore[attr-defined] # it exists
            self.value,
            other,
            where=self.value_mask,
            out=self.value.copy(),
        )
        return self.__shallow_copy_with_new(value)

    def __rmul__(self, other: Any) -> Vector:
        return self * other

    def __truediv__(self, other: Any) -> Vector:
        if other == 0:
            return NotImplemented
        if other == 1 or self.is_empty:
            return self
        if not isinstance(other, int | float | np.floating):
            raise InvalidStateException(
                f"{type(self).__name__} can only be divided with int, float or np.floating",
                invalid_type=type(other).__name__,
            )
        value = np.divide(  # type: ignore[call-overload] # it exists
            self.value,
            other,
            where=self.value_mask,
            out=self.value.copy(),
        )
        return self.__shallow_copy_with_new(value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Vector):
            return False
        return (
            self._denormalizer == other._denormalizer
            and self.negative_filter_indices == other.negative_filter_indices
            and self.value.tobytes() == other.value.tobytes()
        )

    def __hash__(self) -> int:
        return hash((self.value.tobytes(), self.__negative_filter_indices, self._denormalizer))

    def __str__(self) -> str:
        arr_str = np.array_str(  # type: ignore # numpy stub is missing for mypy-pylance
            self.value, precision=NP_PRINT_PRECISION, suppress_small=True
        )
        return f"{type(self).__name__}({arr_str})"

    def __repr__(self) -> str:
        return self.__str__()

    def __shallow_copy_with_new(
        self,
        value: list[float] | list[VectorItemT] | list[np.floating] | NPArray | None = None,
        negative_filter_indices: set[int] | frozenset[int] | None = None,
        denormalizer: float | None = None,
    ) -> Vector:
        value_to_use = self.value if value is None else value
        negative_filter_indices_to_use = (
            self.negative_filter_indices if negative_filter_indices is None else negative_filter_indices
        )
        denormalizer_to_use = self._denormalizer if denormalizer is None else denormalizer
        return Vector(value_to_use, negative_filter_indices_to_use, denormalizer_to_use)

    @staticmethod
    def __init_value(value: Sequence[float] | Sequence[np.floating] | NPArray) -> NPArray:
        if isinstance(value, np.ndarray):
            result = value.astype(VectorItemT, copy=False)
        else:
            result = np.array(list(value), dtype=VectorItemT)
        result.setflags(write=False)  # make immutable
        return result

    @staticmethod
    def __init_negative_filter_indices(
        negative_filter_indices: set[int] | frozenset[int] | None, dimension: int
    ) -> frozenset[int]:
        if not negative_filter_indices:
            return frozenset({})
        if invalid_indices := [idx for idx in negative_filter_indices if idx < 0 or idx >= dimension]:
            raise InvalidStateException(
                "Invalid negative filter indices.",
                invalid_indices=invalid_indices,
                dimension=dimension,
            )
        return frozenset(negative_filter_indices)


PythonTypes = float | int | str | Vector | list[float] | list[str] | BlobInformation
NodeDataTypes = PythonTypes | ImageData
