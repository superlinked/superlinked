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
from functools import reduce

import numpy as np
from beartype.typing import Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationConfig,
    AggregationInputT,
    NumberAggregationInputT,
)


class Aggregation(ABC, Generic[AggregationInputT]):
    def __init__(self, config: AggregationConfig[AggregationInputT] | None = None) -> None:
        self._config = config

    @abstractmethod
    def filter_predicate(
        self, weighted_items: Sequence[Weighted[AggregationInputT]]
    ) -> Sequence[Weighted[AggregationInputT]] | None:
        """
        Returns a list of weighted items that should be included in the aggregation.
        This is used to filter out aggregations that are not needed.
        """

    @abstractmethod
    def aggregate_weighted(
        self,
        weighted_items: Sequence[Weighted[AggregationInputT]],
        context: ExecutionContext,
    ) -> AggregationInputT: ...


class VectorAggregation(Aggregation[Vector]):
    @override
    def filter_predicate(self, weighted_items: Sequence[Weighted[Vector]]) -> Sequence[Weighted[Vector]] | None:
        if filtered_items := [
            weighted
            for weighted in weighted_items
            if weighted.weight != constants.DEFAULT_NOT_AFFECTING_WEIGHT
            and weighted.item is not None
            and not weighted.item.is_empty
        ]:
            return filtered_items
        return None

    @override
    def aggregate_weighted(
        self,
        weighted_items: Sequence[Weighted[Vector]],
        context: ExecutionContext,
    ) -> Vector:
        weighted_vectors = [
            weighted
            for weighted in weighted_items
            if not weighted.item.is_empty and weighted.weight != constants.DEFAULT_NOT_AFFECTING_WEIGHT
        ]
        vectors_with_negative_filters_replaced = (
            weighted.item.replace_negative_filters(constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE) * weighted.weight
            for weighted in weighted_vectors
        )
        aggregated_vector = reduce(lambda a, b: a.aggregate(b), vectors_with_negative_filters_replaced)
        vectors_without_weights = [weighted.item for weighted in weighted_vectors]
        return self.__apply_negative_filter(aggregated_vector, vectors_without_weights)

    def __apply_negative_filter(self, aggregated_vector: Vector, vectors: Sequence[Vector]) -> Vector:
        """
        Applies the previous negative filter on those indices where
        there was a negative filter in all aggregated vectors.
        """
        common_negative_filter_indices = set.intersection(*(set(vector.negative_filter_indices) for vector in vectors))
        negative_filter_vector = self.__calculate_negative_filter_vector(
            vectors, common_negative_filter_indices, aggregated_vector.dimension
        )
        return aggregated_vector.apply_negative_filter(negative_filter_vector)

    def __calculate_negative_filter_vector(
        self, vectors: Sequence[Vector], common_negative_filter_indices: set[int], vector_length: int
    ) -> Vector:
        """
        For each dimension in the intersection of the negative filters
        the value of all of the vector must be the same. Built on that we create a zero-vector
        with these negative filter values.
        """
        if colliding_negative_filter_indices := [
            i for i in common_negative_filter_indices if len({vector.value[i] for vector in vectors}) > 1
        ]:
            raise InvalidStateException(
                "Cannot aggregate vectors having different negative filter values in the same positions.",
                positions=colliding_negative_filter_indices,
            )
        return Vector(
            value=[
                (
                    0.0
                    if i not in common_negative_filter_indices
                    else next(
                        (vector.value[i] for vector in vectors),
                        constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE,
                    )
                )
                for i in range(vector_length)
            ],
            negative_filter_indices=common_negative_filter_indices,
        )


class NumberAggregation(Generic[NumberAggregationInputT], Aggregation[NumberAggregationInputT], ABC):
    @override
    def filter_predicate(
        self, weighted_items: Sequence[Weighted[NumberAggregationInputT]]
    ) -> Sequence[Weighted[NumberAggregationInputT]] | None:
        if filtered_items := [
            weighted
            for weighted in weighted_items
            if weighted.weight != constants.DEFAULT_NOT_AFFECTING_WEIGHT and weighted.item is not None
        ]:
            return filtered_items
        return None

    @override
    def aggregate_weighted(
        self,
        weighted_items: Sequence[Weighted[NumberAggregationInputT]],
        context: ExecutionContext,
    ) -> NumberAggregationInputT:
        weighted_items = [
            weighted
            for weighted in weighted_items
            if weighted.weight != constants.DEFAULT_NOT_AFFECTING_WEIGHT and weighted.item is not None
        ]
        if len(weighted_items) == 0:
            raise InvalidStateException("Cannot aggregate 0 items.")
        return self._aggregate_inputs(weighted_items)

    @abstractmethod
    def _aggregate_inputs(self, inputs: Sequence[Weighted[NumberAggregationInputT]]) -> NumberAggregationInputT:
        pass


class AvgAggregation(NumberAggregation):
    @override
    def _aggregate_inputs(self, inputs: Sequence[Weighted[float | int]]) -> float:
        items = [float(input_.item) for input_ in inputs]
        weights = [input_.weight for input_ in inputs]
        return np.average(  # type: ignore
            items,
            weights=weights,
        )


class MinAggregation(NumberAggregation):
    @override
    def _aggregate_inputs(self, inputs: Sequence[Weighted[float | int]]) -> float:
        items = [float(input_.item) for input_ in inputs]
        return min(items)


class MaxAggregation(NumberAggregation):
    @override
    def _aggregate_inputs(self, inputs: Sequence[Weighted[float | int]]) -> float:
        items = [float(input_.item) for input_ in inputs]
        return max(items)
