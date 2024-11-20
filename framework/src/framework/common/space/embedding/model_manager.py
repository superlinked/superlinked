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

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from beartype.typing import Sequence
from PIL.Image import Image

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.settings import Settings

SENTENCE_TRANSFORMERS_ORG_NAME = "sentence-transformers"
DEFAULT_MODEL_CACHE_DIR = (
    (Path.home() / ".cache" / SENTENCE_TRANSFORMERS_ORG_NAME).absolute().as_posix()
)


class ModelManager(ABC):
    def __init__(self, model_name: str, model_cache_dir: Path | None = None) -> None:
        self._model_name = model_name
        self._model_cache_dir = self.__get_cache_folder(model_cache_dir)

    def embed(self, inputs: Sequence[str | Image | None]) -> list[Vector | None]:
        inputs_without_nones = [input_ for input_ in inputs if input_ is not None]
        if not inputs_without_nones:
            return [None] * len(inputs)
        none_indices = [i for i, input_ in enumerate(inputs) if input_ is None]
        embeddings = self._embed(inputs_without_nones)
        result: list[Vector | None] = [Vector(embedding) for embedding in embeddings]
        for index in none_indices:
            result.insert(index, None)
        return result

    @abstractmethod
    def _embed(
        self, inputs: list[str | Image]
    ) -> list[list[float]] | list[np.ndarray]: ...

    @abstractmethod
    def calculate_length(self) -> int: ...

    def __get_cache_folder(self, model_cache_dir: Path | None) -> Path:
        return model_cache_dir or Path(
            Settings().MODEL_CACHE_DIR or DEFAULT_MODEL_CACHE_DIR
        )
