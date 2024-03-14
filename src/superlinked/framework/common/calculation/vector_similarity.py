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
import numpy.typing as npt


class SimilarityMethod(Enum):
    INNER_PRODUCT = "inner_product"


class VectorSimilarityCalculator:
    def __init__(self, method: SimilarityMethod) -> None:
        self.__method = method

    def calculate_similarity(
        self, vector_a: npt.NDArray[np.float64], vector_b: npt.NDArray[np.float64]
    ) -> float:
        match self.__method:
            case SimilarityMethod.INNER_PRODUCT:
                return self.__calculate_inner_product(vector_a, vector_b)
            case _:
                raise ValueError(f"Unsupported calculation method: {self.__method}")

    def __calculate_inner_product(
        self, vector_a: npt.NDArray[np.float64], vector_b: npt.NDArray[np.float64]
    ) -> float:
        return np.inner(vector_a, vector_b)
