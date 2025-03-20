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

from __future__ import annotations

from enum import Enum

import numpy as np

from superlinked.framework.common.settings import Settings


class VectorComponentPrecision(Enum):
    FLOAT32 = "FLOAT32"
    FLOAT16 = "FLOAT16"

    def to_np_type(self) -> type[np.float32] | type[np.float16]:
        if self is VectorComponentPrecision.FLOAT32:
            return np.float32
        if self is VectorComponentPrecision.FLOAT16:
            return np.float16
        raise ValueError(f"Unsupported vector component precision: {self}")

    @staticmethod
    def init_from_settings() -> VectorComponentPrecision:
        return (
            VectorComponentPrecision.FLOAT32
            if Settings().SUPERLINKED_DISABLE_HALF_PRECISION_EMBEDDING
            else VectorComponentPrecision.FLOAT16
        )
