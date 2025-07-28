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

from collections.abc import Iterable
from itertools import accumulate

import numpy as np
from beartype.typing import Any, Iterator, Sequence, TypeVar

from superlinked.framework.common.const import constants
from superlinked.framework.common.data_types import NPArray, Vector
from superlinked.framework.common.exception import InvalidStateException

T = TypeVar("T")


class CollectionUtil:
    @staticmethod
    def chunk_list(data: Sequence[T], chunk_size: int) -> Iterator[list[T]]:
        return (list(data[i : i + chunk_size]) for i in range(0, len(data), chunk_size))

    @staticmethod
    def get_positive_values_ndarray(value: NPArray) -> NPArray:
        return value[value > constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE]

    @staticmethod
    def convert_single_item_to_list(value: Any) -> list[Any]:
        return list(value) if isinstance(value, Iterable) and not isinstance(value, str) else [value]

    @staticmethod
    def concatenate_vectors(vectors: Sequence[Vector]) -> Vector:
        if not vectors:
            raise InvalidStateException("Cannot concatenate an empty sequence of vectors")

        non_empty_vectors = [v for v in vectors if not v.is_empty]
        if not non_empty_vectors:
            return vectors[0]

        if len(non_empty_vectors) == 1:
            return non_empty_vectors[0]

        dimensions = [v.dimension for v in non_empty_vectors]
        offsets = [0] + list(accumulate(dimensions))[:-1]
        negative_filter_indices = {
            (idx + off) for v, off in zip(non_empty_vectors, offsets) for idx in v.negative_filter_indices
        }
        concatenated_values = np.concatenate([v.value for v in non_empty_vectors])
        return Vector(concatenated_values, negative_filter_indices)

    @staticmethod
    def combine_values_based_on_type(
        items: Iterable[Any],
        condition_matching_values: Iterable[T],
        alternate_values: Iterable[T],
        type_condition: type,
    ) -> list[T]:
        """Recombines values from two iterables based on the type of items in a source iterable."""
        matching_iterator = iter(condition_matching_values)
        alternate_iterator = iter(alternate_values)
        return [
            next(matching_iterator) if isinstance(item, type_condition) else next(alternate_iterator) for item in items
        ]
