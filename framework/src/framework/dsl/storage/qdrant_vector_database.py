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


from beartype.typing import Any

from superlinked.framework.common.precision import Precision
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.qdrant.qdrant_connection_params import (
    QdrantConnectionParams,
)
from superlinked.framework.storage.qdrant.qdrant_vdb_connector import QdrantVDBConnector


class QdrantVectorDatabase(VectorDatabase[QdrantVDBConnector]):
    """
    Qdrant implementation of the VectorDatabase.

    This class provides a Qdrant-based vector database connector.
    """

    # We don't want to force users to use more complex data types.
    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str,
        api_key: str,
        default_query_limit: int = 10,
        timeout: int | None = None,
        search_algorithm: SearchAlgorithm = SearchAlgorithm.FLAT,
        vector_precision: Precision = Precision.FLOAT16,
        prefer_grpc: bool | None = None,
        **extra_params: Any
    ) -> None:
        """
        Initialize the QdrantVectorDatabase.

        Args:
            url (str): The url of the Qdrant server.
            api_key (str): The api key of the Qdrant cluster.
            default_query_limit (int): Default vector search limit, set to Qdrant's default of 10.
            timeout (int | None): Timeout in seconds for Qdrant operations. Default is 5 seconds.
            vector_precision (Precision): Precision to use for storing vectors. Defaults to FLOAT16.
            prefer_grpc (bool | None): Whether to prefer gRPC for Qdrant operations. Default is False.
            **extra_params (Any): Additional parameters for the Qdrant connection.
        """
        super().__init__()
        self._connection_params = QdrantConnectionParams(url, api_key, timeout, prefer_grpc, **extra_params)
        self._settings = VDBSettings(
            default_query_limit=default_query_limit,
            search_algorithm=search_algorithm,
            vector_precision=vector_precision,
        )

    @property
    def _vdb_connector(self) -> QdrantVDBConnector:
        """
        Get the Qdrant vector database connector.

        Returns:
            QdrantVDBConnector: The Qdrant vector database connector instance.
        """
        return QdrantVDBConnector(self._connection_params, self._settings)
