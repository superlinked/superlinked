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

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import numpy.typing as npt

from superlinked.framework.common.data_types import Vector


class Field(ABC):
    @property
    @abstractmethod
    def value(self) -> Any:
        pass

    def __str__(self) -> str:
        return str(self.value)


class VectorField(Field):
    def __init__(self, vector: Vector) -> None:
        self.vector = vector

    @property
    def value(self) -> npt.NDArray[np.float64]:
        return self.vector.value


class TextField(Field):
    def __init__(self, text: str) -> None:
        self.text = text

    @property
    def value(self) -> str:
        return self.text
