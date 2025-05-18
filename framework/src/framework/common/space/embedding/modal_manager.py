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
import numpy as np
import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import UnexpectedResponseException
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import (
    ModelEmbeddingInputT,
    ModelManager,
)
from superlinked.framework.common.util.collection_util import CollectionUtil
from superlinked.framework.common.util.image_util import ImageUtil

logger = structlog.getLogger()


class ModalManager(ModelManager):
    def __init__(self, model_name: str, model_cache_dir: Path | None = None) -> None:
        super().__init__(model_name, model_cache_dir)
        settings = Settings()
        self._modal_cls = modal.Cls.from_name(
            app_name=settings.MODAL_APP_NAME,
            name=settings.MODAL_CLASS_NAME,
            environment_name=settings.MODAL_ENVIRONMENT_NAME,
        )
        self._batch_size = settings.MODAL_BATCH_SIZE
        self._max_retries = settings.MODAL_MAX_RETRIES
        self._retry_delay = settings.MODAL_RETRY_DELAY
        self._image_format = settings.MODAL_IMAGE_FORMAT
        self._image_quality = settings.MODAL_IMAGE_QUALITY

    @override
    def _embed(
        self, inputs: Sequence[ModelEmbeddingInputT], context: ExecutionContext
    ) -> list[list[float]] | list[np.ndarray]:
        text_inputs, image_inputs = self._categorize_inputs(inputs)
        processed_image_inputs = [
            ImageUtil.encode_bytes(image_input, self._image_format, self._image_quality) for image_input in image_inputs
        ]
        image_encodings = self.__send_request(processed_image_inputs)
        text_encodings = self.__send_request(text_inputs)
        logger.info("finished encoding", n_texts=len(text_encodings), n_images=len(image_encodings))
        return CollectionUtil.combine_values_based_on_type(inputs, text_encodings, image_encodings, str)

    @override
    def calculate_length(self) -> int:
        return len(self._modal_cls().embed.remote(["sample"], self._model_name)[0])

    def __send_request(self, inputs: Sequence[str | bytes]) -> list[list[float]]:
        if not inputs:
            return []
        batched_inputs = [inputs[i : i + self._batch_size] for i in range(0, len(inputs), self._batch_size)]
        retry_count = 0
        current_delay = self._retry_delay
        while True:
            try:
                batched_results: list[list[list[float]]] = self._modal_cls().embed.map(
                    batched_inputs, kwargs={"model_name": self._model_name}
                )
                return [item for batch in batched_results for item in batch]
            except Exception as e:  # pylint: disable=broad-exception-caught
                retry_count += 1
                if retry_count >= self._max_retries:
                    logger.error(f"Failed after {self._max_retries} attempts", error=str(e))
                    raise UnexpectedResponseException(
                        f"Failed to get embeddings after {self._max_retries} attempts: {str(e)}"
                    ) from e
                logger.warning(
                    f"Request failed (attempt {retry_count}/{self._max_retries})",
                    error=str(e),
                    retry_delay=current_delay,
                )
                sleep(current_delay)
                current_delay = current_delay * 2

    # TODO: FAB-3342 unify embed methods
    def embed_text(self, inputs: Sequence[str], context: ExecutionContext) -> list[Vector]:
        if not inputs:
            return []
        return [Vector(embedding) for embedding in self._embed(inputs, context)]
