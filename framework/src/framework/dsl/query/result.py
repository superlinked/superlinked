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

from beartype.typing import Any, Sequence

from superlinked.framework.common.util.immutable_model import ImmutableBaseModel


class ResultMetadata(ImmutableBaseModel):
    schema_name: str | None
    search_vector: Sequence[float]
    search_params: dict[str, Any]


class ResultEntryMetadata(ImmutableBaseModel):
    score: float
    partial_scores: Sequence[float]
    vector_parts: Sequence[Sequence[float]]


class ResultEntry(ImmutableBaseModel):
    id: str
    fields: dict[str, Any]
    metadata: ResultEntryMetadata


class QueryResult(ImmutableBaseModel):
    entries: Sequence[ResultEntry]
    metadata: ResultMetadata

    def __str__(self) -> str:
        return str([f"#{i+1} id:{e.id}, object:{e.fields}" for i, e in enumerate(self.entries)])
