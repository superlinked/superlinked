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

from typing_extensions import override

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.query.clause_params import QueryVectorClauseParams
from superlinked.framework.dsl.query.param import IntParamType
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)


@dataclass(frozen=True)
class OverriddenNowClause(SingleValueParamQueryClause):
    @override
    async def get_altered_query_vector_params(
        self,
        query_vector_params: QueryVectorClauseParams,
        index_node_id: str,
        query_schema: IdSchemaObject,
        storage_manager: StorageManager,
    ) -> QueryVectorClauseParams:
        return query_vector_params.set_params(context_time=self.__evaluate())

    @override
    def _get_default_value_param_name(self) -> str:
        return "overridden_now_param__"

    def __evaluate(self) -> int | None:
        if (value := self._get_value()) is not None:
            if not isinstance(value, int):
                raise InvalidInputException(f"'now' should be int, got {type(value).__name__}.")
            return value
        return None

    @classmethod
    def from_param(cls, now: IntParamType) -> OverriddenNowClause:
        return OverriddenNowClause(QueryClause._to_typed_param(now, [int]))
