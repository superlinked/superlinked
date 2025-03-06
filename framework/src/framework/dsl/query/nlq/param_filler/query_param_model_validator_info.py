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

from beartype.typing import Mapping, Sequence

from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_clause import (
    LooksLikeFilterClause,
    QueryClause,
    SpaceWeightClause,
)
from superlinked.framework.dsl.space.space import Space


class QueryParamModelValidatorInfo:
    def __init__(self, clause_collector: NLQClauseCollector) -> None:
        self._space_weight_param_name_by_space = self._extract_space_weight_param_name_by_space(clause_collector)
        self._space_param_name_and_space_weight_param_names = (
            self._extract_space_param_name_and_space_weight_param_names(
                clause_collector, self._space_weight_param_name_by_space
            )
        )
        self._allowed_values_by_param = self._extract_allowed_values(clause_collector)
        looks_like_clause = next(iter(clause_collector.get_clauses_by_type(LooksLikeFilterClause)), None)
        self._weight_param_names = looks_like_clause.weight_param_names if looks_like_clause else None

    @property
    def space_weight_param_name_by_space(self) -> Mapping[Space, str]:
        return self._space_weight_param_name_by_space

    @property
    def space_param_name_and_space_weight_param_names(self) -> Sequence[tuple[str, str]]:
        return self._space_param_name_and_space_weight_param_names

    @property
    def allowed_values_by_param(self) -> Mapping[str, set[ParamInputType]]:
        return self._allowed_values_by_param

    @property
    def weight_param_names(self) -> list[str] | None:
        return self._weight_param_names

    def _extract_space_weight_param_name_by_space(self, clause_collector: NLQClauseCollector) -> dict[Space, str]:
        return {
            clause.space: clause.value_param_name for clause in clause_collector.get_clauses_by_type(SpaceWeightClause)
        }

    def _extract_space_param_name_and_space_weight_param_names(
        self,
        clause_collector: NLQClauseCollector,
        space_weight_param_name_by_space: dict[Space, str],
    ) -> list[tuple[str, str]]:
        spaces = space_weight_param_name_by_space.keys()
        return [
            (space_param_name, space_weight_param_name_by_space[space])
            for clause in clause_collector.clauses
            for space, space_param_name in clause.get_param_name_by_space().items()
            if space in spaces
        ]

    def _extract_allowed_values(self, clause_collector: NLQClauseCollector) -> dict[str, set[ParamInputType]]:
        return {
            QueryClause.get_param(param).name: allowed_values
            for clause in clause_collector.clauses
            for param in clause.params
            if (allowed_values := clause.get_allowed_values(param))
        }
