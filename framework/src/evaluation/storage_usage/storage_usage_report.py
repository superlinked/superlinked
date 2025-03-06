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
from pathlib import Path

import pandas as pd
from beartype.typing import Sequence
from pydantic import SerializationInfo, field_serializer

from superlinked.framework.common.util.immutable_model import ImmutableBaseModel


class IndexedFieldInfo(ImmutableBaseModel):
    type_name: str
    count: int


class PartialResultSource(Enum):
    EAN = "EventAggregationNode"
    AN = "AggregationNode"


class PartialResultInfo(ImmutableBaseModel):
    source: PartialResultSource
    dimension: int


class StorageUsageReportDetail(ImmutableBaseModel):
    title: str
    serialized_data_size: int
    immeasurable_messages_count: int
    indexed_field_types: Sequence[IndexedFieldInfo]
    indexed_vector_size: int
    search_index_type: str
    partial_result_info: Sequence[PartialResultInfo]
    memory_usage: int

    @field_serializer("indexed_field_types")
    def serialize_indexed_field_types(
        self, indexed_field_types: Sequence[IndexedFieldInfo], _: SerializationInfo
    ) -> str:
        return "; ".join(
            [
                f"{indexed_field_type.type_name}: {indexed_field_type.count}"
                for indexed_field_type in indexed_field_types
            ]
        )

    @field_serializer("partial_result_info")
    def serialize_partial_result_info(
        self, partial_result_info: Sequence[PartialResultInfo], _: SerializationInfo
    ) -> str:
        return "; ".join([f"{pri.source.value}: {pri.dimension}" for pri in partial_result_info])


class StorageUsageReport(ImmutableBaseModel):
    report_details: Sequence[StorageUsageReportDetail]

    def to_csv(self, path: Path) -> None:
        if not self.report_details:
            return
        df = pd.DataFrame([res.model_dump() for res in self.report_details])
        df.to_csv(path, index=False)
