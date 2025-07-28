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

from beartype.typing import Any, Callable, Sequence, cast
from topk_sdk.schema import bool as topk_bool
from topk_sdk.schema import f32_vector
from topk_sdk.schema import float as topk_float
from topk_sdk.schema import int as topk_int
from topk_sdk.schema import text, vector_index

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.exception import FeatureNotSupportedException
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.search_index.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)

FieldDescriptor = tuple[str, Any]

TopKFieldTypeByFieldDataType: dict[FieldDataType, Callable[[], Any]] = {
    FieldDataType.DOUBLE: topk_float,
    FieldDataType.INT: topk_int,
    FieldDataType.STRING: text,
    FieldDataType.METADATA_STRING: text,
    FieldDataType.STRING_LIST: text,
    FieldDataType.BOOLEAN: topk_bool,
}

DistanceMetricMap = {
    DistanceMetric.COSINE_SIMILARITY: "cosine",
    DistanceMetric.EUCLIDEAN: "euclidean",
    DistanceMetric.INNER_PRODUCT: "dot_product",
}

SUPERLINKED_INTERNAL_FIELD_PREFIX = "superlinked_internal"
TOPK_ID_FIELD_NAME = "_id"


class TopKFieldDescriptorCompiler:
    @staticmethod
    def compile_descriptors(
        field_descriptors: Sequence[IndexFieldDescriptor],
    ) -> list[FieldDescriptor]:
        return [
            field
            for field in [
                TopKFieldDescriptorCompiler._compile_descriptor(field_descriptor)
                for field_descriptor in field_descriptors
            ]
            if field is not None
        ]

    @staticmethod
    def _compile_descriptor(
        field_descriptor: IndexFieldDescriptor,
    ) -> FieldDescriptor | None:
        if field_descriptor.field_data_type == FieldDataType.VECTOR:
            return TopKFieldDescriptorCompiler._compile_vector_descriptor(field_descriptor)
        return TopKFieldDescriptorCompiler._compile_non_vector_descriptor(field_descriptor)

    @staticmethod
    def _compile_vector_descriptor(
        field_descriptor: IndexFieldDescriptor,
    ) -> FieldDescriptor | None:
        if not isinstance(field_descriptor, VectorIndexFieldDescriptor):
            return None

        if field_descriptor.search_algorithm != SearchAlgorithm.FLAT:
            raise FeatureNotSupportedException(
                f"{field_descriptor.search_algorithm} is not supported by TopK, only FLAT is supported"
            )

        return (
            TopKFieldDescriptorCompiler._encode_field_name(field_descriptor.field_name),
            f32_vector(field_descriptor.field_size).index(
                vector_index(metric=cast(Any, DistanceMetricMap[field_descriptor.distance_metric]))
            ),
        )

    @staticmethod
    def _compile_non_vector_descriptor(
        field_descriptor: IndexFieldDescriptor,
    ) -> FieldDescriptor | None:
        topk_field_cls = TopKFieldTypeByFieldDataType.get(field_descriptor.field_data_type)
        if topk_field_cls:
            return (
                TopKFieldDescriptorCompiler._encode_field_name(field_descriptor.field_name),
                topk_field_cls(),
            )
        return None

    @staticmethod
    def _encode_field_name(field_name: str) -> str:
        # NOTE: In TopK, field names cannot start with "_". Those are reserved for internal use.
        if field_name.startswith("_"):
            return f"{SUPERLINKED_INTERNAL_FIELD_PREFIX}{field_name}"

        return field_name

    @staticmethod
    def _decode_field_name(field_name: str) -> str:
        # NOTE: In TopK, field names cannot start with "_". Those are reserved for internal use.
        if field_name.startswith(SUPERLINKED_INTERNAL_FIELD_PREFIX):
            return field_name[len(SUPERLINKED_INTERNAL_FIELD_PREFIX) :]

        return field_name
