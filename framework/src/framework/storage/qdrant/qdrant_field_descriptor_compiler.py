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

from collections import defaultdict

from beartype.typing import Sequence
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.exception import FeatureNotSupportedException
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search_index.index_field_descriptor import (
    IndexFieldDescriptor,
)

PAYLOAD_SCHEMA_BY_FIELD_DATA_TYPE = {
    FieldDataType.DOUBLE: PayloadSchemaType.FLOAT,
    FieldDataType.INT: PayloadSchemaType.INTEGER,
    FieldDataType.BOOLEAN: PayloadSchemaType.BOOL,
    FieldDataType.STRING: PayloadSchemaType.KEYWORD,
    FieldDataType.METADATA_STRING: PayloadSchemaType.KEYWORD,
    FieldDataType.STRING_LIST: PayloadSchemaType.KEYWORD,
}
INDEXABLE_PAYLOAD_FIELD_TYPES = list(PAYLOAD_SCHEMA_BY_FIELD_DATA_TYPE.keys())

DISTANCE_METRIC_MAP = {
    DistanceMetric.COSINE_SIMILARITY: Distance.COSINE,
    DistanceMetric.EUCLIDEAN: Distance.EUCLID,
    DistanceMetric.INNER_PRODUCT: Distance.DOT,
}


class QdrantFieldDescriptorCompiler:
    @staticmethod
    def create_vector_config(
        index_configs: Sequence[IndexConfig],
    ) -> dict[str, VectorParams]:
        QdrantFieldDescriptorCompiler._validate_index_configs(index_configs)
        return {
            index_config.vector_field_descriptor.field_name: VectorParams(
                size=index_config.vector_field_descriptor.field_size,
                distance=DISTANCE_METRIC_MAP[index_config.vector_field_descriptor.distance_metric],
            )
            for index_config in index_configs
        }

    @staticmethod
    def _validate_index_configs(index_configs: Sequence[IndexConfig]) -> None:
        if any(
            index_config
            for index_config in index_configs
            if index_config.vector_field_descriptor.distance_metric == DistanceMetric.COSINE_SIMILARITY
        ):
            raise FeatureNotSupportedException(
                "Qdrant's cosine similarity isn't supported because a search index with "
                + "cosine distance metric sill always L2 normalize its inputs. That is "
                + "incompatible with Superlinked."
            )

    @staticmethod
    def compile_payload_field_descriptors(
        index_configs: Sequence[IndexConfig],
    ) -> dict[str, PayloadSchemaType]:
        field_descriptors = [
            field_descriptor for index_config in index_configs for field_descriptor in index_config.field_descriptors
        ]
        QdrantFieldDescriptorCompiler.validate_payload_field_types(field_descriptors)
        return {
            field_descriptor.field_name: PAYLOAD_SCHEMA_BY_FIELD_DATA_TYPE[field_descriptor.field_data_type]
            for field_descriptor in field_descriptors
        }

    @staticmethod
    def validate_payload_field_types(
        field_descriptors: Sequence[IndexFieldDescriptor],
    ) -> None:
        if invalid_fields := [
            f"{field_descriptor.field_name}: {field_descriptor.field_data_type.value}"
            for field_descriptor in field_descriptors
            if field_descriptor.field_data_type not in INDEXABLE_PAYLOAD_FIELD_TYPES
        ]:
            indexable_types = ", ".join([fdt.value for fdt in INDEXABLE_PAYLOAD_FIELD_TYPES])
            raise FeatureNotSupportedException(
                "Can only index payload fields of the type(s) " + f"{indexable_types}, got {', '.join(invalid_fields)}."
            )
        field_type_by_field_name = defaultdict(set)
        for field_descriptor in field_descriptors:
            field_type_by_field_name[field_descriptor.field_name].add(field_descriptor.field_data_type)
        if invalid_duplicates := {
            field_name: field_types
            for field_name, field_types in field_type_by_field_name.items()
            if len(field_types) > 1
        }:

            def types_to_ordered_str(data_types: set[FieldDataType]) -> str:
                types = [type_.value for type_ in data_types]
                types.sort()
                return ", ".join(types)

            invalid_duplicates_str = "; ".join(
                [
                    f"{field_name}: ({types_to_ordered_str(field_types)})"
                    for field_name, field_types in invalid_duplicates.items()
                ]
            )
            raise FeatureNotSupportedException(
                f"Cannot index field with multiple field data types, got {invalid_duplicates_str}"
            )
