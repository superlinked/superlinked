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

from beartype.typing import cast
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.dsl.query.clause_params import KNNSearchClauseParams
from superlinked.framework.dsl.query.param import IntParamType
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)


@dataclass(frozen=True)
class LimitClause(SingleValueParamQueryClause):
    def __post_init__(self) -> None:
        super().__post_init__()
        value = QueryClause._get_param_value(self.value_param)
        if value is not None and not isinstance(value, int):
            raise InvalidInputException(f"Limit should be int, got {type(value)}")

    @override
    def get_altered_knn_search_params(self, knn_search_clause_params: KNNSearchClauseParams) -> KNNSearchClauseParams:
        return knn_search_clause_params.set_params(limit=self._get_value())

    @override
    def _get_default_value_param_name(self) -> str:
        return "limit_param__"

    @override
    def _get_value(self) -> int:
        if (value := super()._get_value()) is not None:
            return cast(int, value)
        return constants.DEFAULT_LIMIT

    @classmethod
    def from_param(cls, limit: IntParamType) -> LimitClause:
        return LimitClause(QueryClause._to_typed_param(limit, [int]))
