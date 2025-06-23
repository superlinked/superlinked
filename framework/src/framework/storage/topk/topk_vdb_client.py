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

from collections.abc import Mapping

from beartype.typing import Any, Sequence
from topk_sdk import Client

from superlinked.framework.storage.topk.topk_connection_params import (
    TopKConnectionParams,
)
from superlinked.framework.storage.topk.topk_field_descriptor_compiler import (
    TOPK_ID_FIELD_NAME,
)


class TopKVDBClient:
    """A TopK client wrapper that automatically refreshes the connection when needed."""

    def __init__(self, params: TopKConnectionParams) -> None:
        self._params = params
        self.__client = self._create_client()

    @property
    def client(self) -> Client:
        """
        Property to access the TopK client with connection refresh.
        """
        return self.__client

    def query(self, collection_name: str, query: Any) -> Sequence[dict[str, Any]]:
        return self.__client.collection(collection_name).query(query)

    def get(self, collection_name: str, doc_ids: list[str], fields: list[str] | None = None) -> dict[str, Any]:
        return self.__client.collection(collection_name).get(doc_ids, fields)

    # NOTE: As an early limitation of the system, TopK does not support partial updates yet.
    # This will be fixed in the future.
    #
    # To account for this caviat, before each write, we will `get()` the latest snapshot of
    # the documents. Then we patch the updates on top of the source of truth.
    def upsert_partial(
        self,
        collection_name: str,
        updates: Mapping[str, Mapping[str, Any]],
    ) -> None:
        latest = self.get(collection_name, list(updates.keys()))
        docs = {doc_id: {**doc, **latest.get(doc_id, {})} for doc_id, doc in updates.items()}

        self.__client.collection(collection_name).upsert(
            [{TOPK_ID_FIELD_NAME: doc_id, **doc} for doc_id, doc in docs.items()],
        )

    def _create_client(self) -> Client:
        return Client(
            api_key=self._params.api_key,
            region=self._params.region,
            https=self._params.https,
            host=self._params.host,
        )
