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

from dataclasses import dataclass

import instructor
from beartype.typing import Any
from openai import OpenAI
from pydantic import BaseModel


@dataclass
class OpenAIClientConfig:
    api_key: str
    model: str


class OpenAIClient:
    def __init__(self, config: OpenAIClientConfig) -> None:
        super().__init__()
        open_ai = OpenAI(api_key=config.api_key)
        self._client = instructor.from_openai(open_ai)
        self._openai_model = config.model

    def query(
        self, prompt: str, instructor_prompt: str, response_model: type[BaseModel]
    ) -> dict[str, Any]:
        response: BaseModel = self._client.chat.completions.create(
            model=self._openai_model,
            response_model=response_model,
            max_retries=3,
            messages=[
                {"role": "system", "content": instructor_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        return response.model_dump()
