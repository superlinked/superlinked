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
import sys
import threading
import warnings
from contextlib import contextmanager
from dataclasses import dataclass

import openai as openAILib
import structlog
from beartype.typing import Any, Generator
from pydantic import BaseModel, PydanticDeprecatedSince20

from superlinked.framework.common.settings import settings

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=PydanticDeprecatedSince20,
    )
    import instructor
    from instructor.exceptions import InstructorRetryException

logger = structlog.getLogger()

TEMPERATURE_VALUE: float = 0.0


@dataclass
class OpenAIClientConfig:
    api_key: str
    model: str
    organization: str | None = None
    project: str | None = None
    base_url: str | None = None


@contextmanager
def suppress_tokenizer_warnings() -> Generator[None, Any, None]:
    """
    https://github.com/huggingface/tokenizers/blob/14a07b06e4a8bd8f80d884419ae4630f5a3d8098/bindings/python/src/lib.rs
    This function is necessary because the `tokenizers` library from Hugging Face, which is written in Rust,
    can emit warnings when the current process is forked. This can be common in multiprocessing environments.
    These warnings can clutter the stderr output and are often not useful for end users. Redirecting stderr
    to a pipe and filtering out specific messages is an effective way to handle these warnings.
    """
    msgs_to_filter = [
        "huggingface/tokenizers: The current process just got forked",
        "To disable this warning, you can either:",
        "Avoid using `tokenizers` before the fork if possible",
        "Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)",
    ]
    read_fd, write_fd = os.pipe()
    old_stderr_fd = os.dup(2)
    os.dup2(write_fd, 2)
    os.close(write_fd)

    def filter_stderr() -> None:
        with os.fdopen(read_fd) as f:
            for line in f:
                if not any(msg in line for msg in msgs_to_filter) and sys.__stderr__ is not None:
                    sys.__stderr__.write(line)

    thread = threading.Thread(target=filter_stderr)
    thread.start()
    try:
        yield
    finally:
        os.dup2(old_stderr_fd, 2)
        thread.join()
        os.close(old_stderr_fd)


class OpenAIClient:
    def __init__(self, config: OpenAIClientConfig) -> None:
        super().__init__()
        self._client = instructor.from_openai(
            openAILib.AsyncOpenAI(
                api_key=config.api_key,
                organization=config.organization,
                project=config.project,
                base_url=config.base_url,
            )
        )
        self._openai_model = config.model

    async def query(self, prompt: str, instructor_prompt: str, response_model: type[BaseModel]) -> dict[str, Any]:
        max_retries = settings.SUPERLINKED_NLQ_MAX_RETRIES
        with suppress_tokenizer_warnings():
            try:
                response = await self._client.chat.completions.create(
                    model=self._openai_model,
                    response_model=response_model,
                    max_retries=max_retries,
                    messages=[
                        {"role": "system", "content": instructor_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=TEMPERATURE_VALUE,
                )
            except InstructorRetryException as e:
                logger.warning(
                    f"LLM validation followup failed after {max_retries} retries."
                    " Try increasing SUPERLINKED_NLQ_MAX_RETRIES."
                )
                raise e
        return response.model_dump()
