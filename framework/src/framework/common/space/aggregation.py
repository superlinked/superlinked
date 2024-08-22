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

from abc import abstractmethod
from enum import Enum
from functools import reduce

import numpy as np
from beartype.typing import Any, Generic, Mapping, Sequence, TypeVar
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.exception import NegativeFilterException
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.normalization import L2Norm, Normalization

VALUE_UNAFFECTING_AGGREGATION = 0

AIT = TypeVar("AIT", float, int)


class InputAggregationMode(Enum):
    INPUT_MAXIMUM = "input_maximum"
    INPUT_MINIMUM = "input_minimum"
    INPUT_AVERAGE = "input_average"


class Aggregation:

    def __init__(
        self,
        normalization: Normalization,
    ) -> None:
        self.normalization = normalization

    @abstractmethod
    def aggregate(
        self, vectors: Sequence[Vector], context: ExecutionContext
    ) -> Vector: ...

    @abstractmethod
    def aggregate_weighted(
        self, weighted_vectors: Sequence[Weighted[Vector]], context: ExecutionContext
    ) -> Vector: ...

    def __str__(self) -> str:
        items = {k: str(v) for k, v in self.__dict__.items()} if self.__dict__ else ""
        return f"{self.__class__.__name__}({items})"


class VectorAggregation(Aggregation):

    @override
    def aggregate(self, vectors: Sequence[Vector], context: ExecutionContext) -> Vector:
        vector = self._reduce(vectors)
        return self.normalization.normalize(vector)

    def _aggregate(
        self,
        vectors: Sequence[Weighted[Vector]],
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> Vector:
        vector = self._reduce(vectors)
        return self.normalization.normalize(vector)

    @override
    def aggregate_weighted(
        self,
        weighted_vectors: Sequence[Weighted[Vector]],
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> Vector:
        vector = self._reduce(weighted_vectors)
        return L2Norm().normalize(vector)

    def _reduce(self, vectors: Sequence[Vector | Weighted[Vector]]) -> Vector:
        weighted_vectors = [
            weighted
            for weighted in [
                Weighted(vector) if isinstance(vector, Vector) else vector
                for vector in vectors
            ]
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


class VectorAvg(VectorAggregation):
    @override
    def aggregate(self, vectors: Sequence[Vector], context: ExecutionContext) -> Vector:
        return self._reduce(vectors).normalize(len(vectors))


class InputAggregation(Aggregation, Generic[AIT]):
    def __init__(self, normalization: Normalization, embedding: Embedding) -> None:
        self.embedding = embedding
        super().__init__(normalization)

    @override
    def aggregate(self, vectors: Sequence[Vector], context: ExecutionContext) -> Vector:
        embedding_inputs = [
            self.embedding.inverse_embed(vector, context) for vector in vectors
        ]
        embedding_input = self._aggregate_inputs(embedding_inputs)
        vector = self.embedding.embed(embedding_input, context)
        return vector

    @override
    def aggregate_weighted(
        self, weighted_vectors: Sequence[Weighted[Vector]], context: ExecutionContext
    ) -> Vector:
        weighted_vectors = [
            weighted
            for weighted in weighted_vectors
            if not weighted.item.is_empty
            and weighted.weight is not constants.DEFAULT_NOT_AFFECTING_WEIGHT
        ]
        if len(weighted_vectors) == 1:
            return weighted_vectors[0].item
        embedding_inputs: list[AIT] = [
            self.embedding.inverse_embed(weighted.item, context)
            for weighted in weighted_vectors
        ]
        weights = [weighted.weight for weighted in weighted_vectors]
        embedding_input = np.average(embedding_inputs, weights=weights)
        vector = self.embedding.embed(embedding_input, context)
        return vector

    @abstractmethod
    def _aggregate_inputs(self, inputs: Sequence[AIT]) -> AIT: ...

    @override
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.normalization == other.normalization and isinstance(
                other.embedding, type(self.embedding)
            )
        return False

    def __str__(self) -> str:
        items = (
            {k: str(v) for k, v in self.__dict__.items() if k != "embedding"}
            if self.__dict__
            else ""
        )
        return f"{self.__class__.__name__}({items})"

    @staticmethod
    def from_aggregation_mode(
        aggregation_mode: InputAggregationMode,
        normalization: Normalization,
        embedding: Embedding,
    ) -> InputAggregation[AIT]:
        agg_class = INPUT_TYPE_BY_AGG_MODE.get(aggregation_mode)
        if agg_class is None:
            raise ValueError(f"Unknown aggregation mode: {aggregation_mode}")
        return agg_class(normalization, embedding)


class InputAvg(InputAggregation):
    @override
    def _aggregate_inputs(self, inputs: Sequence[float]) -> float:
        return sum(inputs) / len(inputs)


class InputMin(InputAggregation):
    @override
    def _aggregate_inputs(self, inputs: Sequence[float]) -> float:
        return min(inputs)


class InputMax(InputAggregation):
    @override
    def _aggregate_inputs(self, inputs: Sequence[float]) -> float:
        return max(inputs)


INPUT_TYPE_BY_AGG_MODE: Mapping[InputAggregationMode, type[InputAggregation]] = {
    InputAggregationMode.INPUT_AVERAGE: InputAvg,
    InputAggregationMode.INPUT_MINIMUM: InputMin,
    InputAggregationMode.INPUT_MAXIMUM: InputMax,
}
