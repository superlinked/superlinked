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

from pathlib import Path
from time import sleep

import modal
import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.exception import UnexpectedResponseException
from superlinked.framework.common.space.embedding.model_based.embedding_input import (
    ModelEmbeddingInputT,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine import (
    EmbeddingEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.modal_config import (
    ModalConfig,
)
from superlinked.framework.common.util.concurrent_executor import ConcurrentExecutor
from superlinked.framework.common.util.image_util import ImageUtil

logger = structlog.getLogger()


class ModalEngine(EmbeddingEngine):
    def __init__(self, model_name: str, model_cache_dir: Path | None) -> None:
        super().__init__(model_name, model_cache_dir)
        self._config = ModalConfig()
        self._modal_cls = modal.Cls.from_name(
            app_name=self._config.app_name,
            name=self._config.class_name,
            environment_name=self._config.environment_name,
        )

    @override
    def embed(self, inputs: Sequence[ModelEmbeddingInputT], is_query_context: bool) -> list[list[float]]:
        pre_processed_inputs = self._pre_process_inputs(inputs)
        embeddings = self.__send_request(pre_processed_inputs)
        return embeddings

    def _pre_process_inputs(self, inputs: Sequence[ModelEmbeddingInputT]) -> list[str | bytes]:
        return [
            (
                input_
                if isinstance(input_, str)
                else ImageUtil.encode_bytes(input_, self._config.image_format, self._config.image_quality)
            )
            for input_ in inputs
        ]

    def __send_request(self, inputs: Sequence[str | bytes]) -> list[list[float]]:
        retry_count = 0
        current_delay = self._config.retry_delay
        while True:
            try:
                return ConcurrentExecutor(max_workers=self._config.max_concurrent_batches).execute_batched(
                    func=self._modal_cls().embed.remote,
                    items=inputs,
                    batch_size=self._config.batch_size,
                    additional_args=[self._model_name],
                )
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
                sleep(current_delay)
                current_delay = current_delay * 2
