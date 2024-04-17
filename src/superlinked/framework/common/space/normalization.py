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

from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt


class Normalization(ABC):

    @abstractmethod
    def norm(self, value: npt.NDArray[np.float64]) -> float: ...


class L2Norm(Normalization):
    def norm(self, value: npt.NDArray[np.float64]) -> float:
        return np.linalg.norm(value)  # type: ignore[attr-defined]


class Constant(Normalization):

    def __init__(self, length: float) -> None:
        self.length = length
        self.__validate_length()

    def __validate_length(self) -> None:
        if self.length == 0:
            raise ValueError("Normalization length cannot be zero.")

    def norm(self, value: npt.NDArray[np.float64]) -> float:
        return self.length


class NoNorm(Constant):
    def __init__(self) -> None:
        super().__init__(1)
