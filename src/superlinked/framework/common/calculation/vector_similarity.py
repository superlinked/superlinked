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

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.data_types import NPArray, Vector


class VectorSimilarityCalculator:
    def __init__(self, method: DistanceMetric) -> None:
        self.__method = method

    def calculate_similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        return self.calculate_similarity_np(vector_a.value, vector_b.value)

    def calculate_similarity_np(self, vector_a: NPArray, vector_b: NPArray) -> float:
        match self.__method:
            case DistanceMetric.INNER_PRODUCT:
                return self.__calculate_inner_product(vector_a, vector_b)
            case _:
                raise ValueError(f"Unsupported calculation method: {self.__method}")

    def __calculate_inner_product(self, vector_a: NPArray, vector_b: NPArray) -> float:
        return np.inner(vector_a, vector_b)
