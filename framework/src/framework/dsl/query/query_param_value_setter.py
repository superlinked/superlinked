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

from functools import reduce

import structlog
from beartype.typing import Any, Mapping

from superlinked.framework.dsl.query.clause_params import NLQClauseParams
from superlinked.framework.dsl.query.nlq.nlq_handler import NLQHandler
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor

logger = structlog.getLogger()


class QueryParamValueSetter:
    @classmethod
    def set_values(
        cls, query_descriptor: QueryDescriptor, params: Mapping[str, ParamInputType | None]
    ) -> QueryDescriptor:
        query_descriptor_with_all_clauses = query_descriptor.append_missing_mandatory_clauses()
        cls.validate_params(query_descriptor_with_all_clauses, params)
        altered_query_descriptor = cls.__alter_query_descriptor(query_descriptor_with_all_clauses, params, True)
        nlq_params = cls.__calculate_nlq_params(altered_query_descriptor)
        nlq_altered_query_descriptor = cls.__alter_query_descriptor(altered_query_descriptor, nlq_params, False)
        default_params = cls.__calculate_default_params(nlq_altered_query_descriptor)
        default_altered_query_descriptor = cls.__alter_query_descriptor(
            nlq_altered_query_descriptor, default_params, False
        )
        space_weight_params = default_altered_query_descriptor.get_param_value_for_unset_space_weights()
        return cls.__alter_query_descriptor(default_altered_query_descriptor, space_weight_params, False)

    @classmethod
    def validate_params(cls, query_descriptor: QueryDescriptor, params_to_set: Mapping[str, Any]) -> None:
        all_params_names = {
            QueryClause.get_param(param).name for clause in query_descriptor.clauses for param in clause.params
        }
        unknown_params = set(params_to_set.keys()).difference(all_params_names)
        if unknown_params:
            unknown_params_text = ", ".join(unknown_params)
            raise ValueError(f"Unknown query parameters: {unknown_params_text}.")

    @classmethod
    def __alter_query_descriptor(
        cls,
        query_descriptor: QueryDescriptor,
        params: Mapping[str, ParamInputType | None],
        is_override_set: bool,
    ) -> QueryDescriptor:
        if not params:
            return query_descriptor
        altered_clauses = [clause.alter_param_values(params, is_override_set) for clause in query_descriptor.clauses]
        return query_descriptor.replace_clauses(altered_clauses)

    @classmethod
    def __calculate_nlq_params(cls, query_descriptor: QueryDescriptor) -> dict[str, Any]:
        nlq_params = reduce(
            lambda params, clause: clause.get_altered_nql_params(params), query_descriptor.clauses, NLQClauseParams()
        )
        if nlq_params.client_config is not None and nlq_params.natural_query is not None:
            return NLQHandler(nlq_params.client_config).fill_params(
                nlq_params.natural_query,
                query_descriptor.clauses,
                query_descriptor._space_weight_param_info,
                nlq_params.system_prompt,
            )
        return {}

    @classmethod
    def __calculate_default_params(cls, query_descriptor: QueryDescriptor) -> dict[str, Any]:
        return {
            param_name: default
            for clause in query_descriptor.clauses
            for param_name, default in clause.get_default_value_by_param_name().items()
        }
