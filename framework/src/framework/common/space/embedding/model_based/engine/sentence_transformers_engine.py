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


import warnings
from pathlib import Path

import structlog
from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.precision import Precision
from superlinked.framework.common.space.embedding.model_based.embedding_input import (
    ModelEmbeddingInputT,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine import (
    EmbeddingEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)
from superlinked.framework.common.space.embedding.model_based.model_downloader import (
    SENTENCE_TRANSFORMERS_ORG_NAME,
    ModelDownloader,
)
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message=(
            "Using `TRANSFORMERS_CACHE` is deprecated and "
            "will be removed in v5 of Transformers. Use `HF_HOME` instead."
        ),
    )
    from sentence_transformers import SentenceTransformer

logger = structlog.getLogger()

QUERY_PROMPT_NAME = "query"


class SentenceTransformersEngine(EmbeddingEngine[EmbeddingEngineConfig]):
    def __init__(self, model_name: str, model_cache_dir: Path | None, config: EmbeddingEngineConfig) -> None:
        full_model_name = f"{SENTENCE_TRANSFORMERS_ORG_NAME}/{model_name}" if "/" not in model_name else model_name
        super().__init__(full_model_name, model_cache_dir, config)
        self._model = self._initialize_model()

    @override
    async def embed(self, inputs: Sequence[ModelEmbeddingInputT], is_query_context: bool) -> list[list[float]]:
        prompt_name = self._calculate_prompt_name(self._model, is_query_context)
        return list(
            self._model.encode(
                list(inputs),  # type: ignore[arg-type] # it also accepts Image
                prompt_name=prompt_name,
            )
        )

    def _initialize_model(self) -> SentenceTransformer:
        model_downloader = ModelDownloader()
        cache_dir = model_downloader.get_cache_dir(self._model_cache_dir)
        model_downloader.ensure_model_downloaded(self._model_name, cache_dir)
        device = GpuEmbeddingUtil.get_device()
        cache_dir_text = str(cache_dir)
        model_kwargs = self._get_model_kwargs()
        try:
            model = SentenceTransformer(
                model_name_or_path=self._model_name,
                trust_remote_code=True,
                device=device,
                cache_folder=cache_dir_text,
                local_files_only=True,
                model_kwargs=model_kwargs,
            )
        except OSError:
            logger.warning("Model download issue, forcing re-download.")
            model_downloader.ensure_model_downloaded(self._model_name, cache_dir, force_download=True)
            model = SentenceTransformer(
                model_name_or_path=self._model_name,
                trust_remote_code=True,
                device=device,
                cache_folder=cache_dir_text,
                local_files_only=False,
                model_kwargs=model_kwargs,
            )
        return model

    def _get_model_kwargs(self) -> dict[str, Any]:
        if self._config.precision == Precision.FLOAT16:
            return {"torch_dtype": "float16"}
        if self._config.precision == Precision.FLOAT32:
            return {}
        raise ValueError(f"Unsupported precision: {self._config.precision.value}.")

    def _calculate_prompt_name(self, model: SentenceTransformer, is_query_context: bool) -> str | None:
        return (
            QUERY_PROMPT_NAME if is_query_context and QUERY_PROMPT_NAME in model.prompts else model.default_prompt_name
        )
