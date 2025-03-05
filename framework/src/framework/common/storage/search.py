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


from abc import ABC, abstractmethod

from beartype.typing import Generic, Sequence, TypeVar, cast

from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import VectorFieldData
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)

KNNReturnT = TypeVar("KNNReturnT")
SearchParamsT = TypeVar("SearchParamsT", bound=VDBKNNSearchParams)
QuertT = TypeVar("QuertT")


class Search(ABC, Generic[SearchParamsT, QuertT, KNNReturnT]):
    def knn_search_with_checks(
        self,
        index_config: IndexConfig,
        search_params: SearchParamsT,
    ) -> KNNReturnT:
        self.check_vector_field(index_config, search_params.vector_field)
        self.check_filters(index_config, search_params.filters)
        query = self.build_query(search_params)
        return self.knn_search(index_config, query)

    @abstractmethod
    def build_query(self, search_params: SearchParamsT) -> QuertT:
        pass

    @abstractmethod
    def knn_search(self, index_config: IndexConfig, query: QuertT) -> KNNReturnT:
        pass

    @staticmethod
    def check_vector_field(index_config: IndexConfig, vector_field: VectorFieldData) -> None:
        if vector_field.value is None:
            raise ValidationException("Cannot search with NoneType vector!")
        if index_config.vector_field_descriptor.field_name != vector_field.name:
            raise ValidationException(
                f"Indexed {index_config.vector_field_descriptor.field_name} and"
                + f" searched {vector_field.name} vectors are different."
            )

    @staticmethod
    def check_filters(
        index_config: IndexConfig,
        filters: Sequence[ComparisonOperation[Field]] | None,
    ) -> None:
        if not filters:
            return
        filter_field_names = [cast(Field, filter_._operand).name for filter_ in filters]
        if unindexed_filter_field_names := [
            filter_field_name
            for filter_field_name in filter_field_names
            if filter_field_name not in index_config.indexed_field_names
        ]:
            raise ValidationException(f"Unindexed fields with filter found: {unindexed_filter_field_names}")
