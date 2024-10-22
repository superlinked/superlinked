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
from superlinked.framework.common.exception import NegativeFilterException
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationConfig,
    AggregationInputT,
    NumberAggregationInputT,
)

VALUE_UNAFFECTING_AGGREGATION = 0


class Aggregation(ABC, Generic[AggregationInputT]):
    def __init__(
        self, config: AggregationConfig[AggregationInputT] | None = None
    ) -> None:
        self._config = config

    @abstractmethod
    def aggregate_weighted(
        self,
        weighted_items: Sequence[Weighted[AggregationInputT]],
        context: ExecutionContext,
    ) -> AggregationInputT: ...


class VectorAggregation(Aggregation[Vector]):
    @override
    def aggregate_weighted(
        self,
        weighted_items: Sequence[Weighted[Vector]],
        context: ExecutionContext,
    ) -> Vector:
        weighted_vectors = [
            weighted
            for weighted in weighted_items
            if not weighted.item.is_empty
            and weighted.weight is not constants.DEFAULT_NOT_AFFECTING_WEIGHT
        ]
        vectors_with_negative_filters_replaced = (
            weighted.item.replace_negative_filters(VALUE_UNAFFECTING_AGGREGATION)
            * weighted.weight
            for weighted in weighted_vectors
        )
        aggregated_vector = reduce(
            lambda a, b: a.aggregate(b), vectors_with_negative_filters_replaced
        )
        vectors_without_weights = [weighted.item for weighted in weighted_vectors]
        return self.__apply_negative_filter(aggregated_vector, vectors_without_weights)

    def __apply_negative_filter(
        self, aggregated_vector: Vector, vectors: Sequence[Vector]
    ) -> Vector:
        """
        Applies the previous negative filter on those indices where
        there was a negative filter in all aggregated vectors.
        """
        all_negative_filter_indices = set().union(
            *(vector.negative_filter_indices for vector in vectors)
        )
        return aggregated_vector.copy_with_new(
            negative_filter_indices={
                i
                for i, original_value in enumerate(aggregated_vector.value)
                if original_value == VALUE_UNAFFECTING_AGGREGATION
                and i in all_negative_filter_indices
            }
        ).replace_negative_filters(self.__calculate_negative_filter(vectors))

    def __calculate_negative_filter(self, vectors: Sequence[Vector]) -> int:
        if negative_filter_values := {
            vector.value[negative_filter_index]
            for vector in vectors
            for negative_filter_index in vector.negative_filter_indices
            if vector.value[negative_filter_index] != VALUE_UNAFFECTING_AGGREGATION
        }:
            if len(negative_filter_values) > 1:
                raise NegativeFilterException(
                    f"Cannot aggregate vectors with different negative filter values: {negative_filter_values}."
                )
            return negative_filter_values.pop()
        return VALUE_UNAFFECTING_AGGREGATION


class NumberAggregation(
    Generic[NumberAggregationInputT], Aggregation[NumberAggregationInputT], ABC
):
    @override
    def aggregate_weighted(
        self,
        weighted_items: Sequence[Weighted[NumberAggregationInputT]],
        context: ExecutionContext,
    ) -> NumberAggregationInputT:
        weighted_items = [
            weighted
            for weighted in weighted_items
            if weighted.weight is not constants.DEFAULT_NOT_AFFECTING_WEIGHT
            and weighted.item is not None
        ]
        if len(weighted_items) == 0:
            raise ValueError("Cannot aggregate 0 items.")
        return self._aggregate_inputs(weighted_items)

    @abstractmethod
    def _aggregate_inputs(
        self, inputs: Sequence[Weighted[NumberAggregationInputT]]
    ) -> NumberAggregationInputT:
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
