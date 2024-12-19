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

from collections import defaultdict
from importlib import resources as imp_resources

from beartype.typing import Sequence
from jinja2 import Environment

from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.nlq.param_filler import templates
from superlinked.framework.dsl.query.query_clause import (
    HardFilterClause,
    LooksLikeFilterClause,
    SimilarFilterClause,
    SpaceWeightClause,
)

NLQ_PROMPT_BASE_TEMPLATE_FILE = imp_resources.files(templates) / "nlq_prompt_base.txt"


class QueryParamPromptBuilder:
    @classmethod
    def calculate_instructor_prompt(cls, clause_collector: NLQClauseCollector, system_prompt: str | None = None) -> str:
        base_prompt = cls._read_base_prompt_template()
        env = Environment(trim_blocks=True, lstrip_blocks=True)
        template = env.from_string(base_prompt)
        space_annotation_map = cls._group_space_related_annotations(clause_collector)
        looks_like_clause = next(iter(clause_collector.get_clauses_by_type(LooksLikeFilterClause)), None)
        hard_filter_clauses = clause_collector.get_clauses_by_type(HardFilterClause)
        return template.render(
            space_annotation_map=space_annotation_map,
            looks_like_clause=looks_like_clause,
            hard_filter_clauses=hard_filter_clauses,
            system_prompt=system_prompt,
        )

    @classmethod
    def _read_base_prompt_template(cls) -> str:
        with NLQ_PROMPT_BASE_TEMPLATE_FILE.open("r", encoding="utf-8") as f:
            base_prompt = f.read()
        return base_prompt

    @classmethod
    def _group_space_related_annotations(cls, clause_collector: NLQClauseCollector) -> dict[str, Sequence[str]]:
        annotation_map: defaultdict[str, list[str]] = defaultdict(list[str])
        clause_types: tuple[type[SpaceWeightClause], type[SimilarFilterClause]] = (
            SpaceWeightClause,
            SimilarFilterClause,
        )
        for clause_type in clause_types:
            clauses: Sequence[SpaceWeightClause | SimilarFilterClause] = clause_collector.get_clauses_by_type(
                clause_type
            )
            for clause in clauses:
                annotation_map[clause.space.annotation].append(clause.annotation)
        return dict(annotation_map)
