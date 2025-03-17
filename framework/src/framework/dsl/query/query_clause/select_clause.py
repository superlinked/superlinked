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

from dataclasses import dataclass

import structlog
from beartype.typing import Sequence, cast
from typing_extensions import override

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.clause_params import (
    KNNSearchClauseParams,
    MetadataExtractionClauseParams,
)
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)
from superlinked.framework.dsl.space.space import Space

logger = structlog.getLogger()


@dataclass(frozen=True)
class SelectClause(SingleValueParamQueryClause):
    schema: IdSchemaObject
    vector_parts: Sequence[Space]

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.__validate_fields()

    @override
    def get_altered_knn_search_params(self, knn_search_clause_params: KNNSearchClauseParams) -> KNNSearchClauseParams:
        field_names = self._get_value()
        fields = self._get_selected_fields_by_names(field_names)
        if fields:
            knn_search_clause_params = knn_search_clause_params.set_params(schema_fields_to_return=fields)
        if self.vector_parts:
            knn_search_clause_params = knn_search_clause_params.set_params(should_return_index_vector=True)
        return knn_search_clause_params

    def get_altered_metadata_extraction_params(
        self, metadata_extraction_params: MetadataExtractionClauseParams
    ) -> MetadataExtractionClauseParams:
        if not self.vector_parts:
            return metadata_extraction_params
        vector_part_ids = [vector_part._get_embedding_node(self.schema).node_id for vector_part in self.vector_parts]
        return MetadataExtractionClauseParams(list(metadata_extraction_params.vector_part_ids) + vector_part_ids)

    @override
    def _get_default_value_param_name(self) -> str:
        return "select_param__"

    @override
    def _get_value(self) -> list[str]:
        value = super()._get_value()
        if value is None:
            return []
        return cast(list[str], value)

    def _get_selected_fields_by_names(self, field_names: Sequence[str]) -> list[SchemaField]:
        """We filter out the id field as it is always returned."""
        id_field_name = self.schema.id.name
        filtered_field_names = [name for name in field_names if name != id_field_name]
        return self.schema._get_fields_by_names(filtered_field_names)

    def __validate_fields(self) -> None:
        field_names = self._get_value()
        if self.schema.id.name in field_names:
            logger.info("The id field is automatically included - no need to specify it in the select clause.")
        self._get_selected_fields_by_names(field_names)  # this also validates
        if invalid_vector_parts := [
            type(vector_part).__name__ for vector_part in self.vector_parts if not isinstance(vector_part, Space)
        ]:
            raise ValueError(
                f"{type(self).__name__} can only work with {Space.__name__} vector_parts, got {invalid_vector_parts}"
            )

    @classmethod
    def from_param(
        cls, schema: IdSchemaObject, fields: Param | Sequence[str], vector_parts: Sequence[Space]
    ) -> SelectClause:
        return SelectClause(QueryClause._to_typed_param(fields, [list[str], list[SchemaField]]), schema, vector_parts)
