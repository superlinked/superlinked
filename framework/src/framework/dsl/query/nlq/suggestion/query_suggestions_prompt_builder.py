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

import os

from superlinked.framework.common.util.execution_timer import time_execution
from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.nlq.param_filler.query_param_prompt_builder import (
    QueryParamPromptBuilder,
)

NLQ_SUGGESTION_BASE_TXT_PATH: str = os.path.join(os.path.dirname(__file__), "nlq_suggestion_prompt_base.txt")


class QuerySuggestionsPromptBuilder:
    @classmethod
    @time_execution
    def calculate_instructor_prompt(
        cls,
        clause_collector: NLQClauseCollector,
        system_prompt: str | None,
        feedback: str | None,
        natural_query: str | None,
    ) -> str:
        with open(NLQ_SUGGESTION_BASE_TXT_PATH, "r", encoding="utf-8") as f:
            suggestion_prompt = f.read()
        original_prompt = QueryParamPromptBuilder.calculate_instructor_prompt(clause_collector, system_prompt)
        context_parts = [suggestion_prompt]
        if feedback:
            context_parts.append(f"\nMake suggestions based on the following: {feedback}\n")
        if natural_query:
            context_parts.append(f"\nThe prompt used: {natural_query}\n")
        context_parts.extend(["\n\n######\n", original_prompt])
        return "".join(context_parts)
