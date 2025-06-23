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

from beartype.typing import Any
from topk_sdk.query import field, fn, select

from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.storage.topk.query.topk_filter_builder import (
    TopKFilterBuilder,
)
from superlinked.framework.storage.topk.topk_field_descriptor_compiler import (
    TopKFieldDescriptorCompiler,
)
from superlinked.framework.storage.topk.topk_field_encoder import TopKFieldEncoder

TOPK_VECTOR_DISTANCE_FIELD_NAME = "vector_distance"


@dataclass(frozen=True)
class VectorQuery:
    topk_query: Any


class TopKQueryBuilder:
    def __init__(self, encoder: TopKFieldEncoder) -> None:
        self._encoder = encoder
        self.filter_builder = TopKFilterBuilder(self._encoder)

    def build_query(self, search_params: VDBKNNSearchParams) -> VectorQuery:
        vector_field_name = search_params.vector_field.name
        vector_field_value = search_params.vector_field.value.to_list()

        query = select(
            *[TopKFieldDescriptorCompiler._encode_field_name(field_.name) for field_ in search_params.fields_to_return],
            **{TOPK_VECTOR_DISTANCE_FIELD_NAME: fn.vector_distance(vector_field_name, vector_field_value)},
        )

        if search_params.radius is not None:
            query = query.filter(field(TOPK_VECTOR_DISTANCE_FIELD_NAME) > 1 - search_params.radius)

        if search_params.filters:
            expr = self.filter_builder.build(search_params.filters)
            query = query.filter(expr)

        query = query.topk(field(TOPK_VECTOR_DISTANCE_FIELD_NAME), k=search_params.limit)

        return VectorQuery(query)
