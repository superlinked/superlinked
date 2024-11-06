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

import structlog
from beartype.typing import Any

from superlinked.framework.dsl.query.nlq_param_evaluator import NLQParamEvaluator
from superlinked.framework.dsl.query.query_clause import (
    NLQClause,
    QueryClause,
    WeightedQueryClause,
)
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor

logger = structlog.getLogger()


class QueryParamValueSetter:
    @classmethod
    def set_values(
        cls, query_descriptor: QueryDescriptor, params: dict[str, Any]
    ) -> QueryDescriptor:
        altered_query_descriptor = cls.__alter_query_descriptor(
            query_descriptor, params, True
        )
        nlq_params = cls.__calculate_nlq_params(altered_query_descriptor)
        nlq_altered_query_descriptor = cls.__alter_query_descriptor(
            altered_query_descriptor, nlq_params, False
        )
        return nlq_altered_query_descriptor.append_missing_mandatory_clauses()

    @classmethod
    def __alter_query_descriptor(
        cls,
        query_descriptor: QueryDescriptor,
        params: dict[str, Any],
        is_override_set: bool,
    ) -> QueryDescriptor:
        altered_clauses = [
            cls.__alter_clause(clause, params, is_override_set)
            for clause in query_descriptor.clauses
        ]
        return query_descriptor.replace_clauses(altered_clauses)

    @classmethod
    def __alter_clause(
        cls, clause: QueryClause, params: dict[str, Any], is_override_set: bool
    ) -> QueryClause:
        clause = clause.alter_value(params, is_override_set)
        if isinstance(clause, WeightedQueryClause):
            clause = clause.alter_weight(params, is_override_set)
        return clause

    @classmethod
    def __calculate_nlq_params(
        cls, query_descriptor: QueryDescriptor
    ) -> dict[str, Any]:
        nlq_clause = query_descriptor.get_clause_by_type(NLQClause)
        if nlq_clause is not None and (natural_query := nlq_clause.evaluate()):
            return NLQParamEvaluator(query_descriptor).evaluate_param_infos(
                natural_query, nlq_clause.client_config
            )
        return {}
