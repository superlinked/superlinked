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

from dataclasses import dataclass

from beartype.typing import Sequence

from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)


@dataclass(frozen=True)
class QdrantVDBKNNSearchParams(VDBKNNSearchParams):
    collection_name: str

    @classmethod
    def from_base(
        cls, search_params: VDBKNNSearchParams, collection_name: str, fields_to_return: Sequence[Field]
    ) -> QdrantVDBKNNSearchParams:
        return cls(
            search_params.vector_field,
            search_params.limit,
            fields_to_return,
            search_params.filters,
            search_params.radius,
            collection_name,
        )
