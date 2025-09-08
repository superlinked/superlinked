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

import asyncio
from pathlib import Path

import modal
import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.exception import UnexpectedResponseException
from superlinked.framework.common.space.embedding.model_based.embedding_input import (
    ModelEmbeddingInput,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine import (
    EmbeddingEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.modal_engine_config import (
    ModalEngineConfig,
)

logger = structlog.getLogger()


class ModalEngine(EmbeddingEngine[ModalEngineConfig]):
    def __init__(self, model_name: str, model_cache_dir: Path | None, config: ModalEngineConfig) -> None:
        super().__init__(model_name, model_cache_dir, config)
        client = modal.Client.from_credentials(token_id=self._config.token_id, token_secret=self._config.token_secret)
        modal_cls = modal.Cls.from_name(
            app_name=self._config.app_name,
            name=self._config.class_name,
            environment_name=self._config.environment_name,
        )
        modal_cls.hydrate(client)
        self._embed = modal_cls().embed.remote.aio

    @override
    async def embed(self, inputs: Sequence[ModelEmbeddingInput], is_query_context: bool) -> list[list[float]]:
        retry_count = 0
        current_delay = self._config.retry_delay
        while True:
            try:
                return await asyncio.gather(*[self._embed(input_, self._model_name) for input_ in inputs])
            except Exception as e:  # pylint: disable=broad-exception-caught
                retry_count += 1
                if retry_count >= self._config.max_retries:
                    logger.error(f"Failed after {self._config.max_retries} attempts", error=str(e))
                    raise UnexpectedResponseException(
                        f"Failed to get embeddings after {self._config.max_retries} attempts: {str(e)}"
                    ) from e
                logger.warning(
                    f"Request failed (attempt {retry_count}/{self._config.max_retries})",
                    error=str(e),
                    retry_delay=current_delay,
                )
                await asyncio.sleep(current_delay)
                current_delay = current_delay * 2

    @override
    def is_query_prompt_supported(self) -> bool:
        return False  # TODO FAI-3674 - needs to be added

    @classmethod
    @override
    def _get_clean_model_name(cls, model_name: str) -> str:
        return model_name
