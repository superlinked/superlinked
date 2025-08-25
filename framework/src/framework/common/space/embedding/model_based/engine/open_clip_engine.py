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


import asyncio
import warnings
from pathlib import Path

import structlog
import torch
from beartype.typing import Any, Sequence, cast
from torchvision.transforms.transforms import Compose
from typing_extensions import override

from superlinked.framework.common.exception import (
    NotImplementedException,
    RequestTimeoutException,
)
from superlinked.framework.common.precision import Precision
from superlinked.framework.common.settings import settings
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
    ModelDownloader,
)
from superlinked.framework.common.util.collection_util import CollectionUtil
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil
from superlinked.framework.common.util.image_util import PILImage

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message=(
            "Using `TRANSFORMERS_CACHE` is deprecated and "
            "will be removed in v5 of Transformers. Use `HF_HOME` instead."
        ),
    )
    from open_clip.factory import (
        HF_HUB_PREFIX,
        create_model_and_transforms,
        get_tokenizer,
    )
    from open_clip.model import CLIP

logger = structlog.getLogger()

SUPPORTED_PRECISIONS = [Precision.FLOAT16, Precision.FLOAT32]


class OpenCLIPEngine(EmbeddingEngine[EmbeddingEngineConfig]):
    def __init__(self, model_name: str, model_cache_dir: Path | None, config: EmbeddingEngineConfig) -> None:
        super().__init__(model_name, model_cache_dir, config)
        self._embedding_model, self._preprocess_val = self._get_embedding_model()
        self._tokenizer = get_tokenizer(self._model_name)

    @override
    async def embed(self, inputs: Sequence[ModelEmbeddingInputT], is_query_context: bool) -> list[list[float]]:
        text_inputs = [input_ for input_ in inputs if isinstance(input_, str)]
        image_inputs = [input_ for input_ in inputs if isinstance(input_, PILImage)]
        text_encodings, image_encodings = await asyncio.gather(
            asyncio.to_thread(self._encode_texts_with_no_grad, text_inputs),
            asyncio.to_thread(self._encode_images_with_no_grad, image_inputs),
        )
        encodings = CollectionUtil.combine_values_based_on_type(
            inputs, text_encodings, image_encodings, type_condition=str
        )
        return [self._normalize_encoding(encoding).tolist() for encoding in encodings]

    @override
    def is_query_prompt_supported(self) -> bool:
        return False

    def _encode_texts_with_no_grad(self, text_inputs: Sequence[str]) -> torch.Tensor:
        with torch.no_grad():
            return self.encode_texts(text_inputs)

    def _encode_images_with_no_grad(self, image_inputs: Sequence[PILImage]) -> torch.Tensor:
        with torch.no_grad():
            return self.encode_images(image_inputs)

    def _get_embedding_model(self) -> tuple[CLIP, Compose]:
        device = GpuEmbeddingUtil.get_device()
        model_downloader = ModelDownloader()
        cache_dir = model_downloader.get_cache_dir(self._model_cache_dir)
        if self.__is_model_name_from_hugging_face(self._model_name):
            clean_model_name = self._get_clean_model_name(self._model_name)
            model_downloader.ensure_model_downloaded(clean_model_name, cache_dir)
        model_lock = model_downloader._get_model_lock(self._model_name)
        model_lock_timeout = settings.MODEL_LOCK_TIMEOUT_SECONDS
        if not model_downloader._acquire_lock_with_timeout(model_lock, model_lock_timeout):
            logger.warning(f"Timeout acquiring model lock for {self._model_name} after {model_lock_timeout} seconds")
            raise RequestTimeoutException(f"Timeout acquiring model lock for {self._model_name}")
        cache_dir_text = str(cache_dir)
        try:
            model_and_transforms = create_model_and_transforms(
                self._model_name,
                device=device,
                cache_dir=cache_dir_text,
            )
        except OSError:
            logger.warning("Model download issue, forcing re-download.")
            if self.__is_model_name_from_hugging_face(self._model_name):
                clean_model_name = self._get_clean_model_name(self._model_name)
                model_downloader.ensure_model_downloaded(clean_model_name, cache_dir, force_download=True)
            model_and_transforms = create_model_and_transforms(
                self._model_name,
                device=device,
                cache_dir=cache_dir_text,
            )
        finally:
            model_lock.release()
        model, _, preprocess_val = cast(tuple[CLIP, Any, Compose], model_and_transforms)
        if self._use_half_precision():
            model = model.half()
        return model, preprocess_val

    def _normalize_encoding(self, encoding: torch.Tensor) -> torch.Tensor:
        return encoding / encoding.norm(dim=-1, keepdim=True)

    def encode_texts(self, inputs: Sequence[str]) -> torch.Tensor:
        if not inputs:
            return torch.Tensor()
        tokenized_texts = self._move_tensor_to_model_device(
            self._embedding_model,
            self._tokenizer(list(inputs)),
        )
        results = self._embedding_model.encode_text(tokenized_texts)
        return results

    def encode_images(self, inputs: Sequence[PILImage]) -> torch.Tensor:
        if not inputs:
            return torch.Tensor()
        combined_images_tensor = torch.stack([cast(torch.Tensor, self._preprocess_val(input_)) for input_ in inputs])
        tokenized_images = self._move_tensor_to_model_device(self._embedding_model, combined_images_tensor)
        if self._use_half_precision():
            tokenized_images = tokenized_images.half()
        results = self._embedding_model.encode_image(tokenized_images)
        return results

    def _use_half_precision(self) -> bool:
        if self._config.precision not in SUPPORTED_PRECISIONS:
            raise NotImplementedException("Unsupported precision.", precision=self._config.precision.value)
        return self._config.precision == Precision.FLOAT16

    def _move_tensor_to_model_device(self, embedding_model: CLIP, tensor: torch.Tensor) -> torch.Tensor:
        model_device = next(embedding_model.parameters()).device
        if tensor.device == model_device:
            return tensor
        return tensor.to(model_device)

    @classmethod
    def __is_model_name_from_hugging_face(cls, model_name: str) -> bool:
        return model_name.startswith(HF_HUB_PREFIX)

    @classmethod
    @override
    def _get_clean_model_name(cls, model_name: str) -> str:
        return model_name.replace(HF_HUB_PREFIX, "")
