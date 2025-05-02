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

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import structlog
from beartype.typing import Any, Sequence, cast
from huggingface_hub import HfApi, InferenceClient
from huggingface_hub.inference._providers import PROVIDER_T
from requests import HTTPError
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
from superlinked.framework.common.util.execution_timer import time_execution

logger = structlog.getLogger(__name__)

PROVIDER: PROVIDER_T = "hf-inference"
CONFIG_FILE_NAME = "config.json"
HTTP_PREFIXES = ("http://", "https://")
MODEL_DIMENSION_KEY = "dimension"
MAX_BATCH_SIZE_KEY = "max_batch_size"
DEFAULT_BATCH_SIZE = 32
MODEL_DIM_ALIASES = ["hidden_size", "dim", "embedding_dim", "d_model", "transformer_width", "n_embd"]


class HuggingFaceManager(ModelManager):
    def __init__(self, model_name: str, model_cache_dir: Path | None = None) -> None:
        super().__init__(model_name, model_cache_dir)
        self._embedding_length: int | None = None
        self._is_inference_endpoint = model_name.startswith(HTTP_PREFIXES)
        self._client = self._init_inference_client(model_name)
        self._max_batch_size = self._retrieve_max_batch_size()

    def _retrieve_max_batch_size(self) -> int:
        return self._get_endpoint_info(self._client).get(MAX_BATCH_SIZE_KEY, DEFAULT_BATCH_SIZE)

    @override
    def calculate_length(self) -> int:
        if self._embedding_length is None:
            self._embedding_length = self._get_embedding_dimension(
                self._client, self._model_name, self._is_inference_endpoint
            )
        return self._embedding_length

    # TODO: FAB-3342 unify embed methods
    def embed_text(self, inputs: Sequence[str], context: ExecutionContext) -> list[Vector]:
        if not inputs:
            return []
        return [Vector(embedding) for embedding in self._embed(inputs, context)]

    @override
    @time_execution
    def _embed(
        self, inputs: Sequence[ModelEmbeddingInputT], context: ExecutionContext
    ) -> list[list[float]] | list[np.ndarray]:
        if not inputs:
            return []
        chunked_inputs = CollectionUtil.chunk_list(data=inputs, chunk_size=self._max_batch_size)
        chunked_results = ConcurrentExecutor().execute(
            func=lambda input_: self._client.feature_extraction(text=input_).tolist(),
            args_list=[(input_,) for input_ in chunked_inputs],
            condition=Settings().SUPERLINKED_CONCURRENT_HUGGINGFACE_EMBEDDING,
        )
        return cast(list[list[float]], [item for sublist in chunked_results for item in sublist])

    @classmethod
    @lru_cache(maxsize=32)
    def _get_embedding_dimension(cls, client: InferenceClient, model_name: str, is_inference_endpoint: bool) -> int:
        if is_inference_endpoint:
            if (dimension := cls._get_endpoint_info(client).get(MODEL_DIMENSION_KEY)) is not None:
                return dimension
        else:
            api = HfApi(token=client.token)
            config_info = api.model_info(model_name, files_metadata=True)
            config_siblings = config_info.siblings or []
            has_config = any(file for file in config_siblings if file.rfilename == CONFIG_FILE_NAME)

            if has_config:
                config = json.loads(api.hf_hub_download(model_name, filename=CONFIG_FILE_NAME, token=client.token))
                for field_name in MODEL_DIM_ALIASES:
                    if field_name in config:
                        return config[field_name]
        return cls.__calculate_embedding_dim_from_sample_embedding(client)

    @classmethod
    def _get_endpoint_info(cls, client: InferenceClient) -> dict[str, Any]:
        endpoint_info = {}
        try:
            endpoint_info = client.get_endpoint_info()
        except HTTPError:
            logger.debug("client had no endpoint info")
        return endpoint_info

    def _init_inference_client(self, model_name: str) -> InferenceClient:
        token = Settings().HUGGING_FACE_API_TOKEN
        if self._is_inference_endpoint:
            return InferenceClient(base_url=model_name, token=token, provider=PROVIDER)
        return InferenceClient(model=model_name, token=token, provider=PROVIDER)

    @classmethod
    def __calculate_embedding_dim_from_sample_embedding(cls, client: InferenceClient) -> int:
        return client.feature_extraction("a").shape[-1]
