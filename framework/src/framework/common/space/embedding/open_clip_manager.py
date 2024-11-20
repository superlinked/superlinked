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

import numpy as np
import torch
from beartype.typing import Any, cast
from open_clip.factory import create_model_and_transforms, get_tokenizer
from open_clip.model import CLIP
from open_clip.tokenizer import HFTokenizer, SimpleTokenizer
from PIL.Image import Image
from torchvision.transforms.transforms import Compose  # type:ignore[import-untyped]
from typing_extensions import override

from superlinked.framework.common.space.embedding.model_manager import ModelManager
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil


class OpenClipManager(ModelManager):
    @override
    def calculate_length(self) -> int:
        embedding_model, _ = self._get_embedding_model(0)
        return embedding_model.token_embedding.embedding_dim

    @override
    def _embed(self, inputs: list[str | Image]) -> list[list[float]] | list[np.ndarray]:
        embedding_model, preprocess_val = self._get_embedding_model(len(inputs))
        text_inputs, image_inputs = self._categorize_inputs(inputs)
        self._validate_inputs(inputs)
        with torch.no_grad():
            text_encodings = self.encode_texts(text_inputs, embedding_model)
            image_encodings = self.encode_images(
                image_inputs, embedding_model, preprocess_val
            )
        encodings = self._combine_encodings(inputs, text_encodings, image_encodings)
        return [self._normalize_encoding(encoding).tolist() for encoding in encodings]

    def _get_embedding_model(self, number_of_inputs: int) -> tuple[CLIP, Compose]:
        device_type = GpuEmbeddingUtil.get_device_type(number_of_inputs)
        return OpenClipModelCache.initialize_model(
            self._model_name, device_type, self._model_cache_dir
        )

    def _categorize_inputs(
        self, inputs: list[str | Image]
    ) -> tuple[list[str], list[Image]]:
        text_inputs = [inp for inp in inputs if isinstance(inp, str)]
        image_inputs = [inp for inp in inputs if isinstance(inp, Image)]
        return text_inputs, image_inputs

    def _validate_inputs(self, inputs: list[str | Image]) -> None:
        unsupported_item = next(
            (inp for inp in inputs if not isinstance(inp, (str, Image))), None
        )
        if unsupported_item:
            raise ValueError(
                f"Unsupported Image embedding input type: {type(unsupported_item).__name__}"
            )

    def _combine_encodings(
        self,
        inputs: list[str | Image],
        text_encodings: torch.Tensor,
        image_encodings: torch.Tensor,
    ) -> list[torch.Tensor]:
        text_iter = iter(text_encodings)
        image_iter = iter(image_encodings)
        return [
            next(text_iter) if isinstance(inp, str) else next(image_iter)
            for inp in inputs
        ]

    def _normalize_encoding(self, encoding: torch.Tensor) -> torch.Tensor:
        return encoding / encoding.norm(dim=-1, keepdim=True)

    def encode_texts(self, texts: list[str], embedding_model: CLIP) -> torch.Tensor:
        if not texts:
            return torch.Tensor()
        tokenizer = OpenClipModelCache.initialize_tokenizer(self._model_name)
        texts_tokenized = tokenizer(texts)
        return embedding_model.encode_text(texts_tokenized)

    def encode_images(
        self, images: list[Any], embedding_model: CLIP, preprocess_val: Compose
    ) -> torch.Tensor:
        if not images:
            return torch.Tensor()
        images_to_process = torch.tensor(
            np.stack([preprocess_val(image) for image in images])
        )
        return embedding_model.encode_image(images_to_process)


class OpenClipModelCache:
    @staticmethod
    @lru_cache(maxsize=10)
    def initialize_model(
        model_name: str, device: str, cache_dir: Path
    ) -> tuple[CLIP, Compose]:
        model, _, preprocess_val = cast(
            tuple[CLIP, Any, Compose],
            create_model_and_transforms(
                model_name, device=device, cache_dir=str(cache_dir)
            ),
        )
        return model, preprocess_val

    @staticmethod
    @lru_cache(maxsize=10)
    def initialize_tokenizer(model_name: str) -> HFTokenizer | SimpleTokenizer:
        return get_tokenizer(model_name)
