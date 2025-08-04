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

from enum import Enum

import numpy as np

from superlinked.framework.common.exception import NotImplementedException


class Precision(Enum):
    FLOAT32 = "FLOAT32"
    FLOAT16 = "FLOAT16"

    def to_np_type(self) -> type[np.float32] | type[np.float16]:
        if self is Precision.FLOAT32:
            return np.float32
        if self is Precision.FLOAT16:
            return np.float16
        raise NotImplementedException("Unsupported vector component precision.", precision=self.value)
