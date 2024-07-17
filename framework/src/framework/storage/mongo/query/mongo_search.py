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
from pymongo.collection import Collection
from pymongo.command_cursor import CommandCursor
from typing_extensions import override

from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search import Search
from superlinked.framework.storage.mongo.mongo_field_encoder import MongoFieldEncoder
from superlinked.framework.storage.mongo.query.mongo_query import MongoQuery
from superlinked.framework.storage.mongo.query.mongo_vdb_knn_search_params import (
    MongoVDBKNNSearchParams,
)

MAX_NUMBER_OF_CANDIDATES = 10000


class MongoSearch(Search[MongoVDBKNNSearchParams, MongoQuery, CommandCursor]):
    def __init__(self, collection: Collection, encoder: MongoFieldEncoder) -> None:
        super().__init__()
        self._collection = collection
        self._encoder = encoder

    @override
    def build_query(
        self,
        search_params: MongoVDBKNNSearchParams,
        returned_fields: Sequence[Field],
    ) -> MongoQuery:
        if search_params.num_candidates > MAX_NUMBER_OF_CANDIDATES:
            raise ValueError("Number of nearest neighbors exeeded")
        return (
            MongoQuery(self._encoder)
            # Order is important!
            .add_vector_search_dict(search_params)
            .add_projection_dict(returned_fields)
            .add_radius_filter_dict(search_params.radius)
        )

    @override
    def knn_search(
        self,
        index_config: IndexConfig,
        query: MongoQuery,
    ) -> CommandCursor:
        return self._collection.aggregate(query.query)
