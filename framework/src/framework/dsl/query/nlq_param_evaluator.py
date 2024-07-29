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
        instructor_prompt = self._calculate_instructor_prompt()
        model = self.model_builder.build()
        try:
            client = OpenAIClient(client_config)
            filled_values = client.query(natural_query, instructor_prompt, model)
            return filled_values
        except Exception as e:
            raise QueryException(f"Error executing natural query: {str(e)}") from e

    def _calculate_instructor_prompt(self) -> str:
        affected_spaces_text = self._generate_affected_spaces_text()
        return f"""
        You are the middleman between KNN search, and a user who enters a natural language query to search for neighbors in a vector database.
        To achieve this you have fill up a model, which contains wights and values.
        Your goal is to fill up these values based on the user prompt if the default value is None/null.
        With these fields we will create a knn search vector using our "space"s.
        If the field is not related to any way to the user the prompt, you can use the default value.
        If the user prompt is "I'm looking for a blue dog", search for a field that is related a color field and a field that is related to an animal,
        and set their values "blue" and "dog" respectively. Their weights should be equal and non-zero.
        If the user shows preference for an  attribute, give them bigger weight.
        The name of the field, the corresponding "space" and "schema_field" can help identify what the field is used for.
        {affected_spaces_text}
        """

    def _all_params_have_value_set(self) -> bool:
        return all(param_info.value is not None for param_info in self.param_infos)

    def _generate_affected_spaces_text(self) -> str:
        affected_spaces: set[Space] = {
            param_info.space
            for param_info in self.param_infos
            if param_info.space is not None
        }
        if not affected_spaces:
            return ""
        annotations = {
            type(space).__name__: space.annotation for space in affected_spaces
        }
        return f"Here are the annotations of the space objects we want to use the fields with: {annotations}"
