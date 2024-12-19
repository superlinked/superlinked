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


from beartype.typing import Any, Sequence
from pydantic import BaseModel

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.nlq.open_ai import OpenAIClient, OpenAIClientConfig
from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.nlq.param_filler.query_param_model_builder import (
    QueryParamModelBuilder,
)
from superlinked.framework.dsl.query.nlq.param_filler.query_param_prompt_builder import (
    QueryParamPromptBuilder,
)
from superlinked.framework.dsl.query.nlq.suggestion.query_suggestion_model import (
    QuerySuggestionsModel,
)
from superlinked.framework.dsl.query.nlq.suggestion.query_suggestions_prompt_builder import (
    QuerySuggestionsPromptBuilder,
)
from superlinked.framework.dsl.query.query_clause import QueryClause


class NLQHandler:

    @classmethod
    def fill_params(
        cls,
        natural_query: str,
        query_clauses: Sequence[QueryClause],
        client_config: OpenAIClientConfig,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        clause_collector = NLQClauseCollector(query_clauses)
        if clause_collector.all_params_have_value_set:
            return {}
        model_class = QueryParamModelBuilder.build(clause_collector)
        instructor_prompt = QueryParamPromptBuilder.calculate_instructor_prompt(clause_collector, system_prompt)
        return cls._execute_query(natural_query, instructor_prompt, model_class, client_config)

    @classmethod
    def suggest_improvements(
        cls,
        query_clauses: Sequence[QueryClause],
        natural_query: str | None,
        feedback: str | None,
        client_config: OpenAIClientConfig,
        system_prompt: str | None = None,
    ) -> QuerySuggestionsModel:
        clause_collector = NLQClauseCollector(query_clauses)
        if clause_collector.all_params_have_value_set:
            return QuerySuggestionsModel()
        instructor_prompt = QuerySuggestionsPromptBuilder.calculate_instructor_prompt(
            clause_collector,
            system_prompt,
            feedback,
            natural_query,
        )
        result = cls._execute_query(
            "Analyze the parameter definitions and provide specific improvements.",
            instructor_prompt,
            QuerySuggestionsModel,
            client_config,
        )
        return QuerySuggestionsModel(**result)

    @classmethod
    def _execute_query(
        cls,
        query: str,
        instructor_prompt: str,
        model_class: type[BaseModel],
        client_config: OpenAIClientConfig,
    ) -> dict[str, Any]:
        try:
            client = OpenAIClient(client_config)
            return client.query(query, instructor_prompt, model_class)
        except Exception as e:
            raise QueryException(f"Error executing natural language query: {str(e)}") from e
