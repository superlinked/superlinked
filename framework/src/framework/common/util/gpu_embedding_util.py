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

import torch

from superlinked.framework.common.settings import Settings

CPU_DEVICE_TYPE = "cpu"
CUDA_DEVICE_TYPE = "cuda"
MPS_DEVICE_TYPE = "mps"


class GpuEmbeddingUtil:
    @classmethod
    def should_use_full_precision(cls, device: str) -> bool:
        return Settings().SUPERLINKED_DISABLE_HALF_PRECISION_EMBEDDING or device == CPU_DEVICE_TYPE

    @classmethod
    def should_use_full_precision_for_input(cls, number_of_embeddings: int) -> bool:
        return (
            Settings().SUPERLINKED_DISABLE_HALF_PRECISION_EMBEDDING
            or cls.get_device_type(number_of_embeddings) == CPU_DEVICE_TYPE
        )

    @classmethod
    def get_device_type(cls, number_of_embeddings: int) -> str:
        if cls._should_use_gpu(number_of_embeddings):
            return cls._get_available_gpu_device()
        return CPU_DEVICE_TYPE

    @classmethod
    def _should_use_gpu(cls, number_of_embeddings: int) -> bool:
        return 0 < Settings().GPU_EMBEDDING_THRESHOLD <= number_of_embeddings

    @classmethod
    @lru_cache(3)
    def _get_available_gpu_device(cls) -> str:
        if torch.cuda.is_available():
            return CUDA_DEVICE_TYPE
        if torch.backends.mps.is_available():
            return MPS_DEVICE_TYPE
        return CPU_DEVICE_TYPE
