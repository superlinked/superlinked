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

import numpy as np
from beartype.typing import Sequence, cast
from infinity_client import AuthenticatedClient, Client
from infinity_client.api.default import embeddings
from infinity_client.models import (
    HTTPValidationError,
    OpenAIEmbeddingInputImage,
    OpenAIEmbeddingInputText,
)
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import (
    ModelEmbeddingInputT,
    ModelManager,
)
from superlinked.framework.common.util.collection_util import CollectionUtil
from superlinked.framework.common.util.concurrent_executor import ConcurrentExecutor
from superlinked.framework.common.util.image_util import ImageUtil


class InfinityManager(ModelManager):
    def __init__(self, model_name: str, model_cache_dir: Path | None = None) -> None:
        super().__init__(model_name, model_cache_dir)
        self._client = self.__create_client()

    @override
    def _embed(
        self, inputs: Sequence[ModelEmbeddingInputT], context: ExecutionContext
    ) -> list[list[float]] | list[np.ndarray]:
        text_inputs, image_inputs = self._categorize_inputs(inputs)
        b64_image_inputs = [
            f"data:image/{image_input.format};base64,{ImageUtil.encode_b64(image_input)}"
            for image_input in image_inputs
        ]
        text_encodings, image_encodings = ConcurrentExecutor(max_workers=2).execute(
            func=self.__send_request,
            args_list=[
                (OpenAIEmbeddingInputText(input_=text_inputs, model=self._model_name),),
                (OpenAIEmbeddingInputImage(input_=b64_image_inputs, model=self._model_name),),
            ],
            condition=bool(text_inputs and b64_image_inputs),
        )
        return CollectionUtil.combine_values_based_on_type(inputs, text_encodings, image_encodings, str)

    @override
    def calculate_length(self) -> int:
        result: list[list[float]] = self.__send_request(OpenAIEmbeddingInputText(input_=["a"], model=self._model_name))
        return len(result[0])

    def __send_request(self, body: OpenAIEmbeddingInputImage | OpenAIEmbeddingInputText) -> list[list[float]]:
        if not body.input_:
            return []
        result = embeddings.sync(client=self._client, body=body)
        if isinstance(result, HTTPValidationError) or result is None:
            raise ValueError(f"Invalid response from Infinity API: {result}")
        sorted_embeddings = [embedding_obj.embedding for embedding_obj in sorted(result.data, key=lambda x: x.index)]
        return cast(list[list[float]], sorted_embeddings)

    def __create_client(self) -> Client | AuthenticatedClient:
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
