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

from __future__ import annotations

from pathlib import Path

import structlog
from beartype.typing import Mapping, Sequence

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.embedding.model_based.embedding_input import (
    ModelEmbeddingInputT,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine import (
    EmbeddingEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)
from superlinked.framework.common.space.embedding.model_based.engine.hugging_face_engine import (
    HuggingFaceEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.modal_engine import (
    ModalEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.open_clip_engine import (
    HF_HUB_PREFIX,
    OpenCLIPEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.sentence_transformers_engine import (
    SentenceTransformersEngine,
)
from superlinked.framework.common.space.embedding.model_based.model_dimension_cache import (
    MODEL_DIMENSION_BY_NAME,
)
from superlinked.framework.common.space.embedding.model_based.model_handler import (
    ModelHandler,
    ModelHandlerType,
    TextModelHandler,
)
from superlinked.framework.common.telemetry.telemetry_registry import TelemetryRegistry

ENGINE_BY_HANDLER: Mapping[ModelHandlerType, type[EmbeddingEngine]] = {
    TextModelHandler.SENTENCE_TRANSFORMERS: SentenceTransformersEngine,
    TextModelHandler.HUGGING_FACE: HuggingFaceEngine,
    TextModelHandler.MODAL: ModalEngine,
    ModelHandler.SENTENCE_TRANSFORMERS: SentenceTransformersEngine,
    ModelHandler.HUGGING_FACE: HuggingFaceEngine,
    ModelHandler.OPEN_CLIP: OpenCLIPEngine,
    ModelHandler.MODAL: ModalEngine,
}

logger = structlog.getLogger()


class EmbeddingEngineManager:
    def __init__(self) -> None:
        self._engines: dict[str, EmbeddingEngine] = {}
        self._telemetry = TelemetryRegistry()

    def get_engine(
        self,
        model_handler: ModelHandlerType,
        model_name: str,
        model_cache_dir: Path | None,
        config: EmbeddingEngineConfig,
    ) -> EmbeddingEngine:
        """
        Get or create an embedding engine based on the provided config.
        Returns existing engine if one with matching parameters exists.
        """
        engine_key = self.calculate_engine_key(model_handler, model_name, model_cache_dir, config)
        if engine_key in self._engines:
            return self._engines[engine_key]
        if engine_type := ENGINE_BY_HANDLER.get(model_handler):
            engine = engine_type(model_name, model_cache_dir, config)
            self._engines[engine_key] = engine
            return engine
        raise ValueError(f"Unsupported model handler: {model_handler.value}")

    @classmethod
    def calculate_engine_key(
        cls,
        model_handler: ModelHandlerType,
        model_name: str,
        model_cache_dir: Path | None,
        config: EmbeddingEngineConfig,
    ) -> str:
        clean_model_name = cls._get_clean_model_name(model_handler, model_name)
        parts = [model_handler.value, clean_model_name, config, model_cache_dir]
        engine_key = ":".join(str(part) for part in parts if part is not None)
        return engine_key

    @classmethod
    def _get_clean_model_name(cls, model_handler: ModelHandlerType, model_name: str) -> str:
        if cls._is_sentence_transformers_model_without_prefix(model_handler, model_name):
            return f"sentence-transformers/{model_name}"
        return model_name.replace(HF_HUB_PREFIX, "")

    @classmethod
    def _is_sentence_transformers_model_without_prefix(cls, model_handler: ModelHandlerType, model_name: str) -> bool:
        return (
            model_handler in [TextModelHandler.SENTENCE_TRANSFORMERS, ModelHandler.SENTENCE_TRANSFORMERS]
            and "/" not in model_name
        )

    def clear_engines(self) -> None:
        self._engines.clear()

    async def embed(  # pylint: disable=too-many-arguments
        self,
        model_handler: ModelHandlerType,
        model_name: str,
        inputs: Sequence[ModelEmbeddingInputT],
        is_query_context: bool,
        model_cache_dir: Path | None,
        config: EmbeddingEngineConfig,
    ) -> list[Vector]:
        if not inputs:
            return []
        engine = self.get_engine(model_handler, model_name, model_cache_dir, config)
        labels = {
            "model_name": model_name,
            "handler": model_handler.value,
            "is_query_context": str(is_query_context),
            "precision": config.precision.value,
        }
        self._telemetry.record_metric("embeddings_total", len(inputs), labels=labels)
        with self._telemetry.span("embedding_engine.embed", attributes=labels):
            embeddings = await engine.embed(inputs, is_query_context)
        return [Vector(embedding) for embedding in embeddings]

    async def calculate_length(
        self,
        model_handler: ModelHandlerType,
        model_name: str,
        model_cache_dir: Path | None,
        config: EmbeddingEngineConfig,
    ) -> int:
        clean_model_name = self._get_clean_model_name(model_handler, model_name)
        if clean_model_name in MODEL_DIMENSION_BY_NAME:
            length = MODEL_DIMENSION_BY_NAME[clean_model_name]
            return length
        length = await self.get_engine(model_handler, model_name, model_cache_dir, config).length
        logger.info("Consider caching model dimension.", model_name=clean_model_name, dimension=length)
        return length
