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

import requests  # type: ignore
from beartype.typing import Sequence
from requests.auth import HTTPDigestAuth

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.exception import UnexpectedResponseException
from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)
from superlinked.framework.storage.mongo.search_index.dto import (
    CreateSearchIndexRequest,
    IndexField,
    ListIndicesResponse,
    VectorIndexField,
)
from superlinked.framework.storage.mongo.search_index.mongo_admin_params import (
    MongoAdminParams,
)

SimilarityByDistanceMetric: dict[DistanceMetric, str] = {
    DistanceMetric.EUCLIDEAN: "euclidean",
    DistanceMetric.COSINE_SIMILARITY: "cosine",
    DistanceMetric.INNER_PRODUCT: "dotProduct",
}

TIMEOUT_S = 10


class MongoSearchIndexManager:

    def __init__(
        self, admin_params: MongoAdminParams, timeout_s: int | None = TIMEOUT_S
    ) -> None:
        self.__cluster_name = admin_params.cluster_name
        self.__project_id = admin_params.project_id
        self.__auth = HTTPDigestAuth(
            admin_params.admin_api_user, admin_params.admin_api_password
        )
        self.__base_url = (
            "https://cloud.mongodb.com/api/atlas/v2/groups"
            + f"/{self.__project_id}/clusters/{self.__cluster_name}/fts/indexes"
        )
        self.__timeout_s = timeout_s

    def create_search_index(
        self,
        database_name: str,
        collection_name: str,
        index_name: str,
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
    ) -> None:
        data = CreateSearchIndexRequest(
            database=database_name,
            collectionName=collection_name,
            name=index_name,
            fields=self._compile_index_field_descriptors(
                vector_field_descriptor, field_descriptors
            ),
        )
        resp = requests.post(
            self.__base_url,
            data=data.model_dump_json(),
            auth=self.__auth,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.atlas.2023-01-01+json",
            },
            timeout=self.__timeout_s,
        )
        if resp.status_code != 200:
            raise UnexpectedResponseException(
                {
                    "msg": "Cannot create search index.",
                    "status_code": resp.status_code,
                    "content": resp.content,
                }
            )

    def drop_search_index(
        self, database_name: str, collection_name: str, index_name: str
    ) -> None:
        index_id_by_name = self.get_search_index_ids_by_name(
            database_name, collection_name
        )
        if index_id := index_id_by_name.get(index_name):
            resp = requests.delete(
                f"{self.__base_url}/{index_id}",
                auth=self.__auth,
                headers={"Accept": "application/vnd.atlas.2023-01-01+json"},
                timeout=self.__timeout_s,
            )
            if resp.status_code != 202:
                raise UnexpectedResponseException(
                    {
                        "msg": f"Cannot drop search index ({index_name}).",
                        "status_code": resp.status_code,
                        "content": resp.content,
                    }
                )

    def get_search_index_ids_by_name(
        self,
        database_name: str,
        collection_name: str,
    ) -> dict[str, str]:
        resp = requests.get(
            f"{self.__base_url}/{database_name}/{collection_name}",
            auth=self.__auth,
            headers={"Accept": "application/vnd.atlas.2023-01-01+json"},
            timeout=self.__timeout_s,
        )
        if resp.status_code != 200:
            raise UnexpectedResponseException(
                {
                    "msg": (
                        "Cannot list search indices for the given "
                        + f"database.collection ({database_name}.{collection_name})."
                    ),
                    "status_code": resp.status_code,
                    "content": resp.content,
                }
            )
        results = [ListIndicesResponse(**result_dict) for result_dict in resp.json()]
        return {result.name: result.indexID for result in results}

    def _compile_index_field_descriptors(
        self,
        vector_field_descriptor: VectorIndexFieldDescriptor,
        field_descriptors: Sequence[IndexFieldDescriptor],
    ) -> Sequence[IndexField]:
        vector_field = VectorIndexField(
            type="vector",
            path=vector_field_descriptor.field_name,
            numDimensions=vector_field_descriptor.field_size,
            similarity=SimilarityByDistanceMetric[
                vector_field_descriptor.distance_metric
            ],
        )
        filter_fields = [
            IndexField(type="filter", path=field_descriptor.field_name)
            for field_descriptor in field_descriptors
        ]
        return filter_fields + [vector_field]
