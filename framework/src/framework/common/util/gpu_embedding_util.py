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

import torch

from superlinked.framework.common.util.lazy_property import lazy_property


class GpuEmbeddingUtil:
    def __init__(self, gpu_embedding_threshold: int) -> None:
        self._gpu_embedding_threshold = gpu_embedding_threshold

    def is_above_gpu_embedding_threshold(self, number_of_embeddings: int) -> bool:
        return number_of_embeddings >= self._gpu_embedding_threshold

    @lazy_property
    def gpu_device_type(self) -> str | None:
        device_type = None
        if torch.cuda.is_available():
            device_type = "cuda"
        elif torch.backends.mps.is_available():
            device_type = "mps"
        return device_type

    @lazy_property
    def is_gpu_embedding_enabled(self) -> bool:
        return self.gpu_device_type is not None and self._gpu_embedding_threshold > 0
