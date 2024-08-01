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
from beartype.typing import cast
from huggingface_hub.file_download import (  # type:ignore[import-untyped]
    repo_folder_name,
)
from sentence_transformers import SentenceTransformer
from torch import Tensor
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.interface.has_default_vector import HasDefaultVector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization

SENTENCE_TRANSFORMERS_ORG_NAME = "sentence-transformers"
SENTENCE_TRANSFORMERS_MODEL_DIR: Path = (
    Path.home() / ".cache" / SENTENCE_TRANSFORMERS_ORG_NAME
)


class SentenceTransformerEmbedding(Embedding[str], HasLength, HasDefaultVector):
    def __init__(self, model_name: str, normalization: Normalization) -> None:
        local_files_only = self._model_is_downloaded(model_name)
        self.model = SentenceTransformer(
            model_name,
            trust_remote_code=True,
            local_files_only=local_files_only,
            # device="cpu",
            cache_folder=str(SENTENCE_TRANSFORMERS_MODEL_DIR),
        )
        # albert-base-v1
        self.__normalization = normalization
        self.__length = self.model.get_sentence_embedding_dimension() or 0

    def _model_is_downloaded(self, model_name: str) -> bool:
        return bool(model_name) and (
            (SENTENCE_TRANSFORMERS_MODEL_DIR / model_name).exists()
            or self._get_model_folder_path(model_name).exists()
        )

    def _get_model_folder_path(self, model_name: str) -> Path:
        repo_id = (
            SENTENCE_TRANSFORMERS_ORG_NAME + "/" + model_name
            if "/" not in model_name
            else model_name
        )
        return SENTENCE_TRANSFORMERS_MODEL_DIR / repo_folder_name(
            repo_id=repo_id, repo_type="model"
        )

    def embed_multiple(self, inputs: list[str]) -> list[Vector]:
        embeddings = self.model.encode(inputs) if inputs else []
        return [self.__to_vector(embedding) for embedding in embeddings]

    @override
    def embed(
        self,
        input_: str,
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> Vector:
        return self.embed_multiple([input_])[0]

    @property
    def length(self) -> int:
        return self.__length

    @property
    @override
    def default_vector(self) -> Vector:
        return Vector([0.0] * self.length)

    def __to_vector(self, embedding: list[Tensor] | np.ndarray | Tensor) -> Vector:
        vector_input = cast(np.ndarray, embedding).astype(np.float64)
        vector = Vector(vector_input)
        return vector.normalize(self.__normalization.norm(vector_input))
