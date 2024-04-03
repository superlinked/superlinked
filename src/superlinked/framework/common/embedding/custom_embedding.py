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
import numpy.typing as npt

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength


class CustomEmbedding(HasLength):
    def __init__(self, length: int) -> None:
        self.__length: int = length

    def transform(self, array: npt.NDArray[np.float64]) -> Vector:
        return Vector(array).normalize()

    @property
    def length(self) -> int:
        return self.__length
