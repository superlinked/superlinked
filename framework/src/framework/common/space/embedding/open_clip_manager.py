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
import torch
from beartype.typing import Any, Sequence
from open_clip.model import CLIP
from torchvision.transforms.transforms import Compose  # type:ignore[import-untyped]
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.space.embedding.model_manager import (
    ModelEmbeddingInputT,
    ModelManager,
)
from superlinked.framework.common.space.embedding.open_clip_model_cache import (
    OpenClipModelCache,
)
from superlinked.framework.common.util.collection_util import CollectionUtil
from superlinked.framework.common.util.execution_timer import time_execution
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil

logger = structlog.getLogger(__name__)


class OpenClipManager(ModelManager):
    @override
    def calculate_length(self) -> int:
        embedding_model, _ = self._get_embedding_model(0)
        return len(self.encode_texts([""], embedding_model)[0])

    @override
    @time_execution
    def _embed(
        self, inputs: Sequence[ModelEmbeddingInputT], context: ExecutionContext
    ) -> list[list[float]] | list[np.ndarray]:
        embedding_model, preprocess_val = self._get_embedding_model(len(inputs))
        text_inputs, image_inputs = self._categorize_inputs(inputs)
        with torch.no_grad():
            text_encodings = self.encode_texts(text_inputs, embedding_model)
            image_encodings = self.encode_images(image_inputs, embedding_model, preprocess_val)
        encodings = CollectionUtil.combine_values_based_on_type(inputs, text_encodings, image_encodings, str)
        return [self._normalize_encoding(encoding).tolist() for encoding in encodings]

    def _get_embedding_model(self, number_of_inputs: int) -> tuple[CLIP, Compose]:
        device_type = GpuEmbeddingUtil.get_device_type(number_of_inputs)
        logger.debug(
            "initialize model", model_name=self._model_name, device_type=device_type, cache_dir=self._model_cache_dir
        )
        model = OpenClipModelCache.initialize_model(self._model_name, device_type, self._model_cache_dir)
        return model

    def _normalize_encoding(self, encoding: torch.Tensor) -> torch.Tensor:
        return encoding / encoding.norm(dim=-1, keepdim=True)

    @time_execution
    def encode_texts(self, texts: list[str], embedding_model: CLIP) -> torch.Tensor:
        if not texts:
            return torch.Tensor()
        tokenizer = OpenClipModelCache.initialize_tokenizer(self._model_name)
        texts_tokenized = self._move_tensor_to_model_device(embedding_model, tokenizer(texts))
        if not GpuEmbeddingUtil.should_use_full_precision_for_input(len(texts)):
            texts_tokenized = texts_tokenized.half()
        return embedding_model.encode_text(texts_tokenized)

    @time_execution
    def encode_images(self, images: list[Any], embedding_model: CLIP, preprocess_val: Compose) -> torch.Tensor:
        if not images:
            return torch.Tensor()
        combined_images_tensor = torch.stack([preprocess_val(image) for image in images])
        images_to_process = self._move_tensor_to_model_device(embedding_model, combined_images_tensor)
        if not GpuEmbeddingUtil.should_use_full_precision_for_input(len(images)):
            images_to_process = images_to_process.half()
        return embedding_model.encode_image(images_to_process)

    def _move_tensor_to_model_device(self, embedding_model: CLIP, tensor: torch.Tensor) -> torch.Tensor:
        model_device = next(embedding_model.parameters()).device
        if tensor.device == model_device:
            return tensor
        logger.debug(
            "moved tensor",
            embedding_type="image",
            new_device=model_device,
            model_name=self._model_name,
            old_device=tensor.device,
        )
        return tensor.to(model_device)
