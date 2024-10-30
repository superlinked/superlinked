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

from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.redis.redis_connection_params import (
    RedisConnectionParams,
)
from superlinked.framework.storage.redis.redis_vdb_connector import RedisVDBConnector


class RedisVectorDatabase(VectorDatabase[RedisVDBConnector]):
    """
    Redis implementation of the VectorDatabase.

    This class provides a Redis-based vector database connector.
    """

    def __init__(
        self, host: str, port: int, default_query_limit: int = 10, **extra_params: Any
    ) -> None:
        """
        Initialize the RedisVectorDatabase.

        Args:
            host (str): The hostname of the Redis server.
            port (int): The port number of the Redis server.
            default_query_limit (int): Default vector search limit, set to Redis's default of 10.
            **extra_params (Any): Additional parameters for the Redis connection.
        """
        super().__init__()
        self._connection_params = RedisConnectionParams(host, port, **extra_params)
        self._settings = VDBSettings(default_query_limit)

    @property
    def _vdb_connector(self) -> RedisVDBConnector:
        """
        Get the Redis vector database connector.

        Returns:
            RedisVDBConnector: The Redis vector database connector instance.
        """
        return RedisVDBConnector(self._connection_params, self._settings)
