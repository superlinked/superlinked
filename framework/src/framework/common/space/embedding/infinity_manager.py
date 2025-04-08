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

from functools import lru_cache
from pathlib import Path

from beartype.typing import Sequence, cast
from infinity_client import AuthenticatedClient, Client
from infinity_client.api.default import embeddings
from infinity_client.models import (
    HTTPValidationError,
    OpenAIEmbeddingInputText,
    OpenAIEmbeddingResult,
)
from numpy import ndarray
from PIL.Image import Image
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import ModelManager


class InfinityManager(ModelManager):
    def __init__(self, model_name: str, model_cache_dir: Path | None = None) -> None:
        super().__init__(model_name, model_cache_dir)
        self._client = self.__create_client()

    @override
    def _embed(self, inputs: Sequence[str | Image], context: ExecutionContext) -> list[list[float]] | list[ndarray]:
        return self.__send_request(inputs)

    @override
    @lru_cache(maxsize=32)
    def calculate_length(self) -> int:
        result: list[list[float]] = self.__send_request(["a"])
        return len(result[0])

    def __send_request(self, inputs: Sequence[str | Image]) -> list[list[float]]:
        with self._client as client:
            body = OpenAIEmbeddingInputText.from_dict(
                {
                    "input": inputs,
                    "model": self._model_name,
                }
            )
            result = embeddings.sync(client=client, body=body)
            if isinstance(result, HTTPValidationError):
                raise ValueError(f"Invalid response from Infinity API: {result}")
            result = cast(OpenAIEmbeddingResult, result)

        sorted_embeddings = [embedding_obj.embedding for embedding_obj in sorted(result.data, key=lambda x: x.index)]
        if not all(
            isinstance(embedding, list) and all(isinstance(value, float) for value in embedding)
            for embedding in sorted_embeddings
        ):
            raise ValueError(f"{type(self).__name__}'s embedding result is not a list of lists of floats.")
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
