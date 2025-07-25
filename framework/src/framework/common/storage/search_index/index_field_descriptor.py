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

from dataclasses import dataclass

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.precision import Precision
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)


@dataclass(frozen=True)
class IndexFieldDescriptor:
    field_data_type: FieldDataType
    field_name: str


class VectorIndexFieldDescriptor(IndexFieldDescriptor):
    def __init__(
        self,
        field_name: str,
        field_size: int,
        distance_metric: DistanceMetric,
        search_algorithm: SearchAlgorithm,
        vector_precision: Precision,
    ) -> None:
        super().__init__(FieldDataType.VECTOR, field_name)
        self.field_size = field_size
        self.distance_metric = distance_metric
        self.search_algorithm = search_algorithm
        self.vector_precision = vector_precision
