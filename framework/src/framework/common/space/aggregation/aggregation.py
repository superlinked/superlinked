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

import numpy as np
from beartype.typing import Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import NPArray, Vector, VectorItemT
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
    def aggregate_weighted(self, weighted_items: Sequence[Weighted[Vector]], context: ExecutionContext) -> Vector:
        weighted_vectors = [
            weighted
            for weighted in weighted_items
            if not weighted.item.is_empty and weighted.weight != constants.DEFAULT_NOT_AFFECTING_WEIGHT
        ]
        if not weighted_vectors:
            return Vector.empty_vector()
        if len(weighted_vectors) == 1:
            return weighted_vectors[0].item * weighted_vectors[0].weight
        result_value = np.zeros_like(weighted_vectors[0].item.value, dtype=VectorItemT)
        for weighted in weighted_vectors:
            result_value += (
                np.where(weighted.item.value_mask, weighted.item.value, constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE)
                * weighted.weight
            )
        index_to_negative_filter = self.__calculate_index_to_negative_filter(weighted_vectors, result_value)
        for index, filter_value in index_to_negative_filter.items():
            result_value[index] = filter_value
        return Vector(result_value, set(index_to_negative_filter.keys()))

    def __calculate_index_to_negative_filter(
        self, weighted_vectors: Sequence[Weighted[Vector]], result_value: NPArray
    ) -> dict[int, float]:
        index_to_negative_filter: dict[int, float] = {}
        for weighted in weighted_vectors:
            for i in weighted.item.negative_filter_indices:
                negative_filter = weighted.item.value[i]
                if i in index_to_negative_filter and index_to_negative_filter[i] != negative_filter:
                    raise InvalidStateException(
                        f"Cannot aggregate vectors having different negative filter values at index {i}"
                    )
                if result_value[i] == constants.DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE:
                    index_to_negative_filter[i] = negative_filter
        return index_to_negative_filter


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
