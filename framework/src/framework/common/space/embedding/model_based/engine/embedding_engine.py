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

from abc import abstractmethod
from pathlib import Path

from beartype.typing import Generic, Sequence, TypeVar

from superlinked.framework.common.space.embedding.model_based.embedding_input import (
    ModelEmbeddingInputT,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)
from superlinked.framework.common.util.lazy_property import async_lazy_property

EmbeddingEngineConfigT = TypeVar("EmbeddingEngineConfigT", bound=EmbeddingEngineConfig)


class EmbeddingEngine(Generic[EmbeddingEngineConfigT]):
    def __init__(self, model_name: str, model_cache_dir: Path | None, config: EmbeddingEngineConfigT) -> None:
        self._model_name = model_name
        self._model_cache_dir = model_cache_dir
        self._config = config

    @abstractmethod
    async def embed(self, inputs: Sequence[ModelEmbeddingInputT], is_query_context: bool) -> list[list[float]]: ...

    @abstractmethod
    def is_query_prompt_supported(self) -> bool: ...

    @async_lazy_property
    async def length(self) -> int:
        embedding_results = await self.embed([""], is_query_context=True)
        return len(embedding_results[0])

    @property
    def key(self) -> str:
        return self.calculate_key(self._model_name, self._model_cache_dir, self._config)

    @classmethod
    @abstractmethod
    def _get_clean_model_name(cls, model_name: str) -> str:
        pass

    @classmethod
    def calculate_key(cls, model_name: str, model_cache_dir: Path | None, config: EmbeddingEngineConfig) -> str:
        clean_model_name = cls._get_clean_model_name(model_name)
        parts = [cls.__name__, clean_model_name, config, model_cache_dir]
        engine_key = ":".join(str(part) for part in parts if part is not None)
        return engine_key
