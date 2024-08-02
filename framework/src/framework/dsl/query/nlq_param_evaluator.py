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

from beartype.typing import Any, Sequence
from pydantic import BaseModel

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.nlq.open_ai import OpenAIClient, OpenAIClientConfig
from superlinked.framework.dsl.query.nlq_pydantic_model_builder import (
    NLQPydanticModelBuilder,
)
from superlinked.framework.dsl.query.query_param_information import ParamInfo
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["NLQParamEvaluator"] = False

QUERY_MODEL_NAME = "QueryModel"


class NLQParamEvaluator:
    def __init__(self, param_infos: Sequence[ParamInfo]) -> None:
        self.param_infos = param_infos
        self.model_builder = NLQPydanticModelBuilder(self.param_infos)

    def evaluate_param_infos(
        self, natural_query: str | None, client_config: OpenAIClientConfig | None
    ) -> dict[str, Any]:
        if natural_query is None or self._all_params_have_value_set():
            return {}
        if client_config is None:
            raise QueryException(
                "Natural language query supplied without client config."
            )
        model_class = self.model_builder.build()
        instructor_prompt = self._calculate_instructor_prompt(model_class)
        try:
            client = OpenAIClient(client_config)
            filled_values = client.query(natural_query, instructor_prompt, model_class)
            return filled_values
        except Exception as e:
            raise QueryException(f"Error executing natural query: {str(e)}") from e

    def _all_params_have_value_set(self) -> bool:
        return all(param_info.value is not None for param_info in self.param_infos)

    def _calculate_instructor_prompt(self, model_class: type[BaseModel]) -> str:
        persona_description = """You are the middleman between KNN search,
        and a user who enters a natural language query to search for neighbors in a vector database."""
        context_text = """To achieve this you have fill up a model, which contains wights and values.
        With these fields we will create a knn search vector using our "space"s.
        If the field is not related to any way to the user the prompt, you can use the default value.
        If the user prompt is "I'm looking for a blue dog", search for a field that is related a color field and a field that is related to an animal,
        and set their values "blue" and "dog" respectively. Their weights should be equal and non-zero.
        If the user shows preference for an  attribute, give them bigger weight.
        The name of the field, the corresponding "space" and "schema_field" can help identify what the field is used for.
        """
        affected_spaces_text = self._generate_affected_spaces_text(model_class)
        action_text = "Fill up the weights and values based on the user prompt if the default value is None/null."
        instructor_prompt = "\n####\n".join(
            (
                self._without_line_breaks(persona_description),
                self._without_line_breaks(context_text),
                affected_spaces_text,
                action_text,
            )
        )
        return instructor_prompt

    def _group_param_infos_by_space_and_annotation(
        self,
    ) -> dict[str, dict[Space, list[ParamInfo]]]:
        param_infos_by_space_by_annotation: defaultdict[
            str, defaultdict[Space, list[ParamInfo]]
        ] = defaultdict(lambda: defaultdict(list))
        for param_info in self.param_infos:
            if param_info.space is not None:
                annotation = self._without_line_breaks(param_info.space.annotation)
                param_infos_by_space_by_annotation[annotation][param_info.space].append(
                    param_info
                )
        return dict(param_infos_by_space_by_annotation)

    def _generate_affected_spaces_text(self, model_class: type[BaseModel]) -> str:
        param_infos_by_space_by_annotation = (
            self._group_param_infos_by_space_and_annotation()
        )
        param_infos_without_space = [
            param_info for param_info in self.param_infos if param_info.space is None
        ]
        space_related_text = (
            self._calculate_space_related_text(
                model_class, param_infos_by_space_by_annotation
            )
            if param_infos_by_space_by_annotation
            else None
        )
        non_space_related_text_with_description = (
            self._calculate_non_space_related_text(
                model_class, param_infos_without_space
            )
            if param_infos_without_space
            else None
        )
        return "\n###\n".join(
            part
            for part in (space_related_text, non_space_related_text_with_description)
            if part is not None
        )

    def _calculate_non_space_related_text(
        self, model_class: type[BaseModel], param_infos_without_space: list[ParamInfo]
    ) -> str:
        field_details_text = "\n".join(
            (
                self._calculate_field_details_text(model_class, param_info)
                for param_info in param_infos_without_space
            )
        )
        return f"Here are some details of the fields that need an exact value to be set set:\n{field_details_text}"

    def _calculate_space_related_text(
        self,
        model_class: type[BaseModel],
        param_infos_by_space_by_annotation: dict[str, dict[Space, list[ParamInfo]]],
    ) -> str:
        space_text = "\n##\n".join(
            (
                self._generate_space_text(annotation, param_infos_by_space, model_class)
                for annotation, param_infos_by_space in param_infos_by_space_by_annotation.items()
            )
        )
        return f"Here are some details of the space objects we will use and their corresponding fields:\n\n{space_text}"

    def _generate_space_text(
        self,
        annotation: str,
        param_infos_by_space: dict[Space, list[ParamInfo]],
        model_class: type[BaseModel],
    ) -> str:
        space_field_text = "\n\n".join(
            (
                self._generate_space_field_text(space, param_infos, model_class)
                for space, param_infos in param_infos_by_space.items()
            )
        )
        return f"{space_field_text}\n\nWith the space description of:\n{annotation}"

    def _generate_space_field_text(
        self, space: Space, param_infos: list[ParamInfo], model_class: type[BaseModel]
    ) -> str:
        field_details = "\n".join(
            (
                self._calculate_field_details_text(model_class, param_info)
                for param_info in param_infos
            )
        )
        return f"{type(space).__name__}_{hash(space)}:\n{field_details}"

    def _calculate_field_details_text(
        self, model_class: type[BaseModel], param_info: ParamInfo
    ) -> str:
        model_field_info = model_class.model_fields[param_info.name]
        field_type = (
            model_field_info.annotation.__name__
            if model_field_info.annotation
            else "any"
        )
        is_weight_text = "weight" if param_info.is_weight else "value"
        field_detail_parts = [
            f" - {param_info.name} is a {is_weight_text}",
            (
                f" that has to be {param_info.op.value.replace('_', ' ')}"
                if param_info.op
                else ""
            ),
            f" to {field_type} type",
            (
                f" for the field named {param_info.schema_field.name}"
                if param_info.schema_field
                else ""
            ),
            (
                f" with the following description: {param_info.description}"
                if param_info.description
                else ""
            ),
        ]
        return "".join(part for part in field_detail_parts if part)

    def _without_line_breaks(self, text: str) -> str:
        python_multiline_string_delimiter = "\n        "
        return text.replace(python_multiline_string_delimiter, " ")
