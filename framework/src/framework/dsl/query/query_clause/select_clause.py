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
from superlinked.framework.dsl.query.clause_params import KNNSearchClauseParams
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)

logger = structlog.getLogger()


@dataclass(frozen=True)
class SelectClause(SingleValueParamQueryClause):
    schema: IdSchemaObject

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.__validate_fields()

    @override
    def get_altered_knn_search_params(self, partial_params: KNNSearchClauseParams) -> KNNSearchClauseParams:
        field_names = self._get_value()
        fields = self._get_selected_fields_by_names(field_names)
        if fields:
            return partial_params.set_params(schema_fields_to_return=fields)
        return partial_params

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

    @classmethod
    def from_param(cls, schema: IdSchemaObject, param: Param | Sequence[str]) -> SelectClause:
        return SelectClause(QueryClause._to_typed_param(param, [list[str], list[SchemaField]]), schema)
