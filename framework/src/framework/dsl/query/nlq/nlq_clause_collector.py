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

from collections.abc import Sequence

from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.dsl.query.nlq.nlq_compatible_clause_handler import (
    NLQCompatibleClauseHandler,
)
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.space_weight_param_info import SpaceWeightParamInfo


class NLQClauseCollector:
    def __init__(self, clauses: Sequence[QueryClause], space_weight_param_info: SpaceWeightParamInfo) -> None:
        self.__clause_handlers = NLQCompatibleClauseHandler.from_clauses(clauses)
        self.__space_weight_param_info = space_weight_param_info

    @property
    def clause_handlers(self) -> Sequence[NLQCompatibleClauseHandler]:
        return self.__clause_handlers

    @property
    def space_weight_param_info(self) -> SpaceWeightParamInfo:
        return self.__space_weight_param_info

    @property
    def all_params_have_value_set(self) -> bool:
        return all(
            isinstance(param, Evaluated)
            for clause_handler in self.__clause_handlers
            for param in clause_handler.clause.params
        )
