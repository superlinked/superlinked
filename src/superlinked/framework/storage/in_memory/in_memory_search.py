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

from collections import defaultdict
from typing import Any, cast

from beartype.typing import Sequence

from superlinked.framework.common.calculation.vector_similarity import (
    VectorSimilarityCalculator,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import VectorFieldData
from superlinked.framework.common.storage.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.storage.in_memory.exception import (
    VectorFieldDimensionException,
    VectorFieldTypeException,
)
from superlinked.framework.storage.in_memory.index_config import IndexConfig


class InMemorySearch:
    def search(
        self,
        vdb: defaultdict[str, dict[str, Any]],
        filters: Sequence[ComparisonOperation[Field]],
        has_fields: Sequence[Field],
    ) -> Sequence[str]:
        return [
            row_id
            for row_id, values in vdb.items()
            if InMemorySearch._is_subset(values, filters, has_fields)
        ]

    def knn_search(
        self,
        index_config: IndexConfig,
        vdb: defaultdict[str, dict[str, Any]],
        search_params: VDBKNNSearchParams,
    ) -> list[tuple[str, float]]:
        self._check_vector_field(index_config, search_params.vector_field)
        self._check_filters(index_config, search_params.filters)
        filtered_vectors = self._filter_indexed_vectors(
            vdb,
            search_params.vector_field,
            search_params.filters,
        )
        similarities = self._calculate_similarities(
            index_config.vector_similarity_calculator,
            search_params.vector_field.value,
            filtered_vectors,
        )
        sorted_similarities = self._sort_similarities(
            similarities,
            search_params.radius,
        )
        return (
            sorted_similarities[: search_params.limit]
            if search_params.limit
            else sorted_similarities
        )

    def _check_vector_field(
        self, index_config: IndexConfig, vector_field: VectorFieldData
    ) -> None:
        if vector_field.value is None:
            raise ValidationException("Cannot search with none-type vector!")
        if index_config.vector_field_name != vector_field.name:
            raise ValidationException(
                f"Indexed {index_config.vector_field_name} and"
                + f" searched {vector_field.name} vectors are different!"
            )

    def _check_filters(
        self,
        index_config: IndexConfig,
        filters: Sequence[ComparisonOperation[Field]] | None,
    ) -> None:
        if unindexed_fields := set(
            field_name
            for filter_ in (filters or [])
            if (field_name := cast(Field, filter_._operand).name)
            not in index_config.indexed_field_names
        ):
            raise ValidationException(f"Unindexed fields found: {unindexed_fields}")

    def _filter_indexed_vectors(
        self,
        vdb: dict[str, dict[str, Any]],
        vector_field: VectorFieldData,
        filters: Sequence[ComparisonOperation[Field]] | None,
    ) -> dict[str, Vector]:
        filtered_unchecked_vectors = {
            row_id: values[vector_field.name]
            for row_id, values in vdb.items()
            if InMemorySearch._is_subset(values, filters or [])
            and values.get(vector_field.name) is not None
        }
        filtered_vectors = self._validate_filtered_vectors(
            filtered_unchecked_vectors,
            cast(Vector, vector_field.value),
        )
        return filtered_vectors

    def _validate_filtered_vectors(
        self, filtered_unchecked_vectors: dict[str, Any], vector: Vector
    ) -> dict[str, Vector]:
        if wrong_types := {
            type(value)
            for value in filtered_unchecked_vectors.values()
            if not isinstance(value, Vector)
        }:
            raise VectorFieldTypeException(
                f"Indexed vector field contains non-vectors: {wrong_types}"
            )
        if wrong_dimensions := {
            value
            for value in filtered_unchecked_vectors.values()
            if value.dimension != vector.dimension
        }:
            raise VectorFieldDimensionException(
                f"Indexed vector field contains vectors with wrong dimensions: {wrong_dimensions}"
            )
        return cast(dict[str, Vector], filtered_unchecked_vectors)

    def _calculate_similarities(
        self,
        vector_similarity_calculator: VectorSimilarityCalculator,
        vector: Vector,
        filtered_vectors: dict[str, Vector],
    ) -> dict[str, float]:
        return {
            row_id: vector_similarity_calculator.calculate_similarity(
                filtered_vector, vector
            )
            for row_id, filtered_vector in filtered_vectors.items()
        }

    def _sort_similarities(
        self,
        similarities: dict[str, float],
        radius: float | None,
    ) -> list[tuple[str, float]]:
        return sorted(
            {
                k: similarity
                for k, similarity in similarities.items()
                if not radius or similarity >= (1 - radius)
            }.items(),
            key=lambda x: x[1],
            reverse=True,
        )

    @staticmethod
    def _is_subset(
        raw_entity: dict[str, Any],
        filters: Sequence[ComparisonOperation[Field]],
        has_fields: Sequence[Field] | None = None,
    ) -> bool:
        """
        Return true, if all filters are True to the entity.
        """
        if not (filters or has_fields):
            return True
        return all(
            filter_.evaluate(raw_entity.get(cast(Field, filter_._operand).name))
            for filter_ in filters
        ) and all(
            raw_entity.get(filter_.name) is not None for filter_ in has_fields or []
        )
