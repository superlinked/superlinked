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

import numpy as np
import torch
from beartype.typing import Any, cast
from open_clip.factory import create_model_and_transforms, get_tokenizer
from open_clip.model import CLIP
from PIL.ImageFile import ImageFile
from torchvision.transforms.transforms import Compose  # type:ignore[import-untyped]
from typing_extensions import override

from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_manager import ModelManager
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil


class OpenClipManager(ModelManager):
    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)
        self._tokenizer = get_tokenizer(model_name)
        self._gpu_embedding_util = GpuEmbeddingUtil(Settings().GPU_EMBEDDING_THRESHOLD)
        self._model = self._initialize_model(model_name, "cpu")
        self._bulk_model = (
            self._initialize_model(
                model_name,
                self._gpu_embedding_util.gpu_device_type,
            )
            if self._gpu_embedding_util.is_gpu_embedding_enabled
            else ()
        )

    def _get_embedding_model(self, number_of_inputs: int) -> tuple[CLIP, Compose]:
        return (
            self._bulk_model
            if self._bulk_model
            and self._gpu_embedding_util.is_above_gpu_embedding_threshold(
                number_of_inputs
            )
            else self._model
        )

    @override
    def _embed(
        self, inputs: list[str | ImageFile]
    ) -> list[list[float]] | list[np.ndarray]:
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

    def _categorize_inputs(
        self, inputs: list[str | ImageFile]
    ) -> tuple[list[str], list[ImageFile]]:
        text_inputs = [inp for inp in inputs if isinstance(inp, str)]
        image_inputs = [inp for inp in inputs if isinstance(inp, ImageFile)]
        return text_inputs, image_inputs

    def _validate_inputs(self, inputs: list[str | ImageFile]) -> None:
        unsupported_item = next(
            (inp for inp in inputs if not isinstance(inp, (str, ImageFile))), None
        )
        if unsupported_item:
            raise ValueError(
                f"Unsupported Image embedding input type: {type(unsupported_item).__name__}"
            )

    def _combine_encodings(
        self,
        inputs: list[str | ImageFile],
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
        texts_tokenized = self._tokenizer(texts)
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

    @classmethod
    @lru_cache(maxsize=128)
    @override
    def calculate_length(cls, model_name: str) -> int:
        embedding_model, _ = cls._initialize_model(model_name, "cpu")
        length = embedding_model.token_embedding.embedding_dim
        return length

    @classmethod
    @lru_cache(maxsize=20)
    def _initialize_model(cls, model_name: str, device: str) -> tuple[CLIP, Compose]:
        model, _, preprocess_val = cast(
            tuple[CLIP, Any, Compose],
            create_model_and_transforms(
                model_name, device=device, cache_dir=str(cls._get_cache_folder())
            ),
        )
        return model, preprocess_val
