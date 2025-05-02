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

from time import sleep

import numpy as np
import structlog
from beartype.typing import Sequence, cast
from infinity_client import AuthenticatedClient, Client
from infinity_client.api.default import embeddings
from infinity_client.models import (
    OpenAIEmbeddingInputImage,
    OpenAIEmbeddingInputText,
    OpenAIEmbeddingResult,
)
from PIL.Image import Image
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
from superlinked.framework.common.util.concurrent_executor import ConcurrentExecutor
from superlinked.framework.common.util.image_util import ImageUtil

logger = structlog.getLogger()


class InfinityManager(ModelManager):
    @override
    def _embed(
        self, inputs: Sequence[ModelEmbeddingInputT], context: ExecutionContext
    ) -> list[list[float]] | list[np.ndarray]:
        text_inputs, image_inputs = self._categorize_inputs(inputs)
        concurrent_executor = ConcurrentExecutor()
        with self.__create_single_use_client() as client:
            image_encodings = concurrent_executor.execute_batched(
                func=self._process_images_in_batch,
                items=image_inputs,
                batch_size=Settings().INFINITY_IMAGE_BATCH_SIZE,
                additional_args=(client,),
            )
            text_encodings = concurrent_executor.execute_batched(
                func=self._process_texts_in_batch,
                items=text_inputs,
                batch_size=Settings().INFINITY_TEXT_BATCH_SIZE,
                additional_args=(client,),
            )
        logger.info("finished encoding", n_texts=len(text_encodings), n_images=len(image_encodings))
        return CollectionUtil.combine_values_based_on_type(inputs, text_encodings, image_encodings, str)

    def _process_images_in_batch(
        self, image_inputs: Sequence[Image], client: AuthenticatedClient | Client
    ) -> list[list[float]]:
        b64_image_inputs = [
            f"data:image/{image_input.format};base64,{ImageUtil.encode_b64(image_input)}"
            for image_input in image_inputs
        ]
        body = OpenAIEmbeddingInputImage(input_=b64_image_inputs, model=self._model_name)
        return self.__send_request(client, body)

    def _process_texts_in_batch(
        self, text_inputs: Sequence[str], client: AuthenticatedClient | Client
    ) -> list[list[float]]:
        return self.__send_request(client, OpenAIEmbeddingInputText(input_=list(text_inputs), model=self._model_name))

    @override
    def calculate_length(self) -> int:
        with self.__create_single_use_client() as client:
            result: list[list[float]] = self.__send_request(
                client, OpenAIEmbeddingInputText(input_=["sample"], model=self._model_name)
            )
        return len(result[0])

    def __send_request(
        self, client: AuthenticatedClient | Client, body: OpenAIEmbeddingInputImage | OpenAIEmbeddingInputText
    ) -> list[list[float]]:
        if not body.input_:
            return []
        max_retries = Settings().INFINITY_MAX_RETRIES
        retry_delay = Settings().INFINITY_RETRY_DELAY
        for attempt in range(max_retries):
            result = embeddings.sync(client=client, body=body)
            if result is not None:
                break
            logger.exception(f"Attempt {attempt + 1}/{max_retries}" f" Response was None.")
            if attempt < max_retries - 1:
                sleep(retry_delay)
            else:
                raise UnexpectedResponseException("Infinity server response was None.")
        result = cast(OpenAIEmbeddingResult, result)
        sorted_embeddings = [embedding_obj.embedding for embedding_obj in sorted(result.data, key=lambda x: x.index)]
        return cast(list[list[float]], sorted_embeddings)

    def __create_single_use_client(self) -> Client | AuthenticatedClient:
        """Returns a context manager that creates a new client instance
        for a single request and automatically handles its lifecycle."""
        settings = Settings()
        if settings.INFINITY_API_URL is None:
            raise ValueError("INFINITY_API_URL is not set in settings.")

        client: AuthenticatedClient | Client
        if settings.INFINITY_API_TOKEN:
            client = AuthenticatedClient(settings.INFINITY_API_URL, token=settings.INFINITY_API_TOKEN)
        else:
            client = Client(settings.INFINITY_API_URL)
        return client

    # TODO: FAB-3342 unify embed methods
    def embed_text(self, inputs: Sequence[str], context: ExecutionContext) -> list[Vector]:
        if not inputs:
            return []
        return [Vector(embedding) for embedding in self._embed(inputs, context)]
