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

from typing import cast

import numpy as np
from sentence_transformers import SentenceTransformer
from torch import Tensor

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength


class SentenceTransformerEmbedding(HasLength):
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)
        self.__length = self.model.get_sentence_embedding_dimension()

    def transform(self, texts: list[str]) -> list[Vector]:
        embeddings = self.model.encode(texts)
        return [self.__to_vector(embedding) for embedding in embeddings]

    @property
    def length(self) -> int:
        return self.__length

    def __to_vector(self, embedding: list[Tensor] | np.ndarray | Tensor) -> Vector:
        return Vector(list(cast(np.ndarray, embedding).astype(np.float32).tolist()))
