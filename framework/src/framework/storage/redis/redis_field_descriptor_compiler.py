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

from beartype.typing import Sequence
from redis.commands.search.field import Field as RedisField
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.field import VectorField as RedisVectorField

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.storage.field_data_type import FieldDataType
from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)

RedisFieldTypeByFieldDataType: dict[FieldDataType, type[RedisField]] = {
    FieldDataType.DOUBLE: NumericField,
    FieldDataType.INT: NumericField,
    FieldDataType.STRING: TextField,
    FieldDataType.STRING_LIST: TagField,
}

DistanceMetricMap = {
    DistanceMetric.COSINE_SIMILARITY: "COSINE",
    DistanceMetric.EUCLIDEAN: "L2",
    DistanceMetric.INNER_PRODUCT: "IP",
}


class RedisFieldDescriptorCompiler:
    @staticmethod
    def compile_descriptors(
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
    ) -> Sequence[RedisField]:
        return [
            field
            for field in [
                RedisFieldDescriptorCompiler._compile_descriptor(field_descriptor)
                for field_descriptor in (
                    [vector_field_descriptor] + list(field_descriptors)
                )
            ]
            if field is not None
        ]

    @staticmethod
    def _compile_descriptor(
        field_descriptor: IndexFieldDescriptor,
    ) -> RedisField | None:
        if field_descriptor.field_data_type == FieldDataType.VECTOR:
            if isinstance(field_descriptor, VectorIndexFieldDescriptor):
                algorithm = field_descriptor.search_algorithm.value
                coordinate_type = field_descriptor.coordinate_type.value
                return RedisVectorField(
                    field_descriptor.field_name,
                    algorithm,
                    {
                        "TYPE": coordinate_type,
                        "DIM": field_descriptor.field_size,
                        "DISTANCE_METRIC": DistanceMetricMap[
                            field_descriptor.distance_metric
                        ],
                    },
                )
        elif redis_field_cls := RedisFieldTypeByFieldDataType.get(
            field_descriptor.field_data_type
        ):
            return redis_field_cls(field_descriptor.field_name, sortable=True)
        return None
