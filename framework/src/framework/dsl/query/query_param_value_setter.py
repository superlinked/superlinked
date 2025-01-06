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
from beartype.typing import Any, Mapping

from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.dsl.query.nlq.nlq_handler import NLQHandler
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_clause import (
    NLQClause,
    NLQSystemPromptClause,
    QueryClause,
    WeightedQueryClause,
)
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor

logger = structlog.getLogger()


class QueryParamValueSetter:
    @classmethod
    def set_values(cls, query_descriptor: QueryDescriptor, params: Mapping[str, ParamInputType]) -> QueryDescriptor:
        query_descriptor_with_all_clauses = query_descriptor.append_missing_mandatory_clauses()
        cls.validate_params(query_descriptor_with_all_clauses, params)
        altered_query_descriptor = cls.__alter_query_descriptor(query_descriptor_with_all_clauses, params, True)
        nlq_params = cls.__calculate_nlq_params(altered_query_descriptor)
        nlq_altered_query_descriptor = cls.__alter_query_descriptor(altered_query_descriptor, nlq_params, False)
        space_weight_params = nlq_altered_query_descriptor.get_param_value_to_set_for_unset_space_weight_clauses()
        return cls.__alter_query_descriptor(nlq_altered_query_descriptor, space_weight_params, False)

    @classmethod
    def validate_params(cls, query_descriptor: QueryDescriptor, params_to_set: Mapping[str, Any]) -> None:
        weight_params = [clause.weight_param for clause in query_descriptor.get_weighted_clauses()]
        value_params = [clause.value_param for clause in query_descriptor.clauses]
        all_params = weight_params + value_params
        param_names = [param.item.name if isinstance(param, Evaluated) else param.name for param in all_params]
        unknown_params = set(params_to_set.keys()) - set(param_names)
        if unknown_params:
            unknown_params_text = ", ".join(unknown_params)
            raise ValueError(f"Unknown query parameters: {unknown_params_text}.")

    @classmethod
    def __alter_query_descriptor(
        cls,
        query_descriptor: QueryDescriptor,
        params: Mapping[str, ParamInputType],
        is_override_set: bool,
    ) -> QueryDescriptor:
        altered_clauses = [cls.__alter_clause(clause, params, is_override_set) for clause in query_descriptor.clauses]
        return query_descriptor.replace_clauses(altered_clauses)

    @classmethod
    def __alter_clause(
        cls, clause: QueryClause, params: Mapping[str, ParamInputType], is_override_set: bool
    ) -> QueryClause:
        clause = clause.alter_value(params, is_override_set)
        if isinstance(clause, WeightedQueryClause):
            clause = clause.alter_weight(params, is_override_set)
        return clause

    @classmethod
    def __calculate_nlq_params(cls, query_descriptor: QueryDescriptor) -> dict[str, Any]:
        nlq_clause = query_descriptor.get_clause_by_type(NLQClause)
        if nlq_clause is not None and (natural_query := nlq_clause.evaluate()):
            nlq_system_prompt_clause = query_descriptor.get_clause_by_type(NLQSystemPromptClause)
            system_prompt = nlq_system_prompt_clause.evaluate() if nlq_system_prompt_clause is not None else None
            return NLQHandler.fill_params(
                natural_query,
                query_descriptor.clauses,
                nlq_clause.client_config,
                system_prompt,
            )
        return {}
