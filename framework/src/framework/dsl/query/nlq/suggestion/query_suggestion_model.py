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

import textwrap

from beartype.typing import Sequence
from pydantic import BaseModel, Field

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QuerySuggestionsModel"] = False


class QuerySuggestionsModel(BaseModel):
    parameter_name_suggestions: list[str] = Field(
        default=[],
        description=(
            "Specific suggestions for renaming parameters to be more intuitive and self-documenting. "
            "Each suggestion should include both the proposed new name and a brief explanation of why "
            "it better describes the parameter's purpose. For example: 'Rename query_text to search_term "
            "to better reflect that it contains the main search terms from user input'."
        ),
    )
    parameter_description_suggestions: list[str] = Field(
        default=[],
        description=(
            "Suggestions for improving parameter descriptions to be more clear and helpful. Each suggestion "
            "should specify the parameter name, its purpose, data type, expected value ranges, and concrete "
            "usage examples. For example: 'Update description_weight description to clarify that it accepts "
            "float values between 0 and 2, where 1 is neutral importance'."
        ),
    )
    clarifying_questions: list[str] = Field(
        default=[],
        description=(
            "Questions that the query creator should answer to provide better context for the LLM "
            "to understand their intent and generate more accurate query parameters. Focus on ambiguous "
            "aspects and request specific examples where helpful."
        ),
    )

    def print(self) -> None:
        """Prints formatted suggestions and clarifying questions."""
        self._print_section("Parameter Name Suggestions", self.parameter_name_suggestions)
        self._print_section("Parameter Description Suggestions", self.parameter_description_suggestions)
        self._print_section("Clarifying Questions", self.clarifying_questions)

    def _print_section(self, title: str, items: Sequence[str]) -> None:
        """Prints a section of items with a title if items exist.

        Args:
            title: The section title to display
            items: List of items to print under the title
        """
        if not items:
            return
        print(f"\n{title}:")
        for item in items:
            wrapped_lines = textwrap.fill(item, width=100, initial_indent="• ", subsequent_indent="  ")
            print(wrapped_lines)
