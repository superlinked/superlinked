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
from itertools import groupby

from beartype.typing import Sequence
from jinja2 import Environment

from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.nlq.param_filler import templates
from superlinked.framework.dsl.query.nlq.param_filler.nlq_annotation import (
    NLQAnnotation,
    NLQAnnotationType,
)

NLQ_PROMPT_BASE_TEMPLATE_FILE = imp_resources.files(templates) / "nlq_prompt_base.txt"


class QueryParamPromptBuilder:
    @classmethod
    def calculate_instructor_prompt(cls, clause_collector: NLQClauseCollector, system_prompt: str | None = None) -> str:
        base_prompt = cls._read_base_prompt_template()
        env = Environment(trim_blocks=True, lstrip_blocks=True)
        template = env.from_string(base_prompt)
        space_annotation_map = cls._group_space_related_annotations(clause_collector)
        nlq_annotations_by_type = QueryParamPromptBuilder.__get_nlq_annotations_by_type(clause_collector)
        space_affecting_annotations = nlq_annotations_by_type.get(NLQAnnotationType.SPACE_AFFECTING)
        exact_value_required_annotations = nlq_annotations_by_type.get(NLQAnnotationType.EXACT_VALUE_REQUIRED)
        return template.render(
            space_annotation_map=space_annotation_map,
            space_affecting_annotations=space_affecting_annotations,
            exact_value_required_annotations=exact_value_required_annotations,
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
        for clause_handler in clause_collector.clause_handlers:
            for space_annotation, annotation in clause_handler.annotation_by_space_annotation.items():
                annotation_map[space_annotation].append(annotation)
        return dict(annotation_map)

    @staticmethod
    def __get_nlq_annotations_by_type(
        clause_collector: NLQClauseCollector,
    ) -> dict[NLQAnnotationType, list[NLQAnnotation]]:
        def get_group_key(annotation: NLQAnnotation) -> NLQAnnotationType:
            return annotation.annotation_type

        def get_sort_key(annotation: NLQAnnotation) -> str:
            return annotation.annotation_type.value

        annotations = [
            annotation_with_type
            for clause_handler in clause_collector.clause_handlers
            for annotation_with_type in clause_handler.nlq_annotations
        ]
        return dict(
            map(lambda item: (item[0], list(item[1])), groupby(sorted(annotations, key=get_sort_key), get_group_key))
        )
