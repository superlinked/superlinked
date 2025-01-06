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

from pymongo.command_cursor import CommandCursor
from pymongo.database import Database
from typing_extensions import override

from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search import Search
from superlinked.framework.storage.mongo_db.mongo_db_field_encoder import (
    MongoDBFieldEncoder,
)
from superlinked.framework.storage.mongo_db.query.mongo_db_query import MongoDBQuery
from superlinked.framework.storage.mongo_db.query.mongo_db_vdb_knn_search_params import (
    MongoDBVDBKNNSearchParams,
)

MAX_NUMBER_OF_CANDIDATES = 10000


class MongoDBSearch(Search[MongoDBVDBKNNSearchParams, MongoDBQuery, CommandCursor]):
    def __init__(self, db: Database, encoder: MongoDBFieldEncoder) -> None:
        super().__init__()
        self._db = db
        self._encoder = encoder

    @override
    def build_query(self, search_params: MongoDBVDBKNNSearchParams) -> MongoDBQuery:
        if search_params.num_candidates > MAX_NUMBER_OF_CANDIDATES:
            raise ValueError("Number of nearest neighbors exeeded")
        return (
            MongoDBQuery(self._encoder, search_params.collection_name)
            # Order is important!
            .add_vector_search_dict(search_params)
            .add_projection_dict(search_params.fields_to_return)
            .add_radius_filter_dict(search_params.radius)
        )

    @override
    def knn_search(
        self,
        index_config: IndexConfig,
        query: MongoDBQuery,
    ) -> CommandCursor:
        return self._db[query.collection_name].aggregate(query.query)
