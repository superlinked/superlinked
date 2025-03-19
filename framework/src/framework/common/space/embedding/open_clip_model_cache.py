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

from beartype.typing import Any, cast
from open_clip.factory import create_model_and_transforms, get_tokenizer
from open_clip.model import CLIP
from open_clip.tokenizer import HFTokenizer, SimpleTokenizer
from torchvision.transforms.transforms import Compose  # type:ignore[import-untyped]

from superlinked.framework.common.settings import Settings
from superlinked.framework.common.util.execution_timer import time_execution
from superlinked.framework.common.util.gpu_embedding_util import GpuEmbeddingUtil


class OpenClipModelCache:
    @staticmethod
    @lru_cache(maxsize=Settings().SUPERLINKED_MODEL_CACHE_SIZE)
    @time_execution
    def initialize_model(model_name: str, device: str, cache_dir: Path) -> tuple[CLIP, Compose]:
        model, _, preprocess_val = cast(
            tuple[CLIP, Any, Compose],
            create_model_and_transforms(
                model_name,
                device=device,
                cache_dir=str(cache_dir),
            ),
        )
        if not GpuEmbeddingUtil.should_use_full_precision(device):
            model = model.half()
        return model, preprocess_val

    @staticmethod
    @lru_cache(maxsize=Settings().SUPERLINKED_MODEL_CACHE_SIZE)
    def initialize_tokenizer(model_name: str) -> HFTokenizer | SimpleTokenizer:
        return get_tokenizer(model_name)
