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


from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.topk.topk_connection_params import (
    TopKConnectionParams,
)
from superlinked.framework.storage.topk.topk_vdb_connector import TopKVDBConnector


class TopKVectorDatabase(VectorDatabase[TopKVDBConnector]):
    """
    TopK implementation of the VectorDatabase.
    This class provides a TopK-based vector database connector.
    """

    def __init__(
        self,
        api_key: str,
        region: str,
        https: bool = True,
        host: str = "topk.io",
        default_query_limit: int = 10,
    ) -> None:
        """
        Initialize the TopKVectorDatabase.
        Args:
            api_key (str): The API key for the TopK server.
            region (str): The region of the TopK server.
            https (bool): Whether to use HTTPS for the TopK server.
            host (str): The host of the TopK server.
            default_query_limit (int): Default vector search limit, set to TopK's default of 10.
        """
        super().__init__()
        self._connection_params = TopKConnectionParams(api_key=api_key, region=region, https=https, host=host)
        self._settings = VDBSettings(default_query_limit=default_query_limit)

    @property
    def _vdb_connector(self) -> TopKVDBConnector:
        """
        Get the TopK vector database connector.
        Returns:
            TopKVDBConnector: The TopK vector database connector instance.
        """
        return TopKVDBConnector(self._connection_params, self._settings)
