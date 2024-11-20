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


import numpy as np
import structlog
from beartype.typing import Sequence
from PIL.Image import Image
from sentence_transformers import SentenceTransformer
from typing_extensions import override

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.embedding.model_manager import ModelManager
from superlinked.framework.common.space.embedding.sentence_transformer_model_cache import (
    SentenceTransformerModelCache,
)
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil

logger = structlog.getLogger()


class SentenceTransformerManager(ModelManager):
    @override
    def _embed(self, inputs: list[str | Image]) -> list[list[float]] | list[np.ndarray]:
        model = self._get_embedding_model(len(inputs))
        embeddings = model.encode(
            inputs,  # type: ignore[arg-type] # it also accepts Image
        )
        return embeddings.tolist()

    @override
    def calculate_length(self) -> int:
        return SentenceTransformerModelCache.calculate_length(
            self._model_name, self._model_cache_dir
        )

    def _get_embedding_model(self, number_of_inputs: int) -> SentenceTransformer:
        device_type = GpuEmbeddingUtil.get_device_type(number_of_inputs)
        return SentenceTransformerModelCache.initialize_model(
            self._model_name, device_type, self._model_cache_dir
        )

    def embed_without_nones(self, inputs: Sequence[str | Image | None]) -> list[Vector]:
        return [input_ for input_ in self.embed(inputs) if input_ is not None]
