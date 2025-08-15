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


from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.connection import BlockingConnectionPool, ConnectionPool

from superlinked.framework.common.settings import ResourceSettings

REDIS_PROTOCOL = 3


class RedisVDBClient:
    """A Redis client wrapper that automatically refreshes the connection when needed."""

    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self.__async_client = self._create_async_client()
        self.__sync_client = self._create_sync_client()

    @property
    def client(self) -> AsyncRedis:
        """
        Property to access the Redis client with connection refresh.
        """
        return self.__async_client

    @property
    def sync_client(self) -> SyncRedis:
        """
        Property to access the Redis client with connection refresh.
        """
        return self.__sync_client

    def _create_sync_client(self) -> SyncRedis:
        return SyncRedis.from_url(self._connection_string, protocol=REDIS_PROTOCOL)

    def _create_async_client(self) -> AsyncRedis:
        settings = ResourceSettings().vector_database
        pool: ConnectionPool = BlockingConnectionPool.from_url(
            self._connection_string,
            protocol=REDIS_PROTOCOL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT_SECONDS,
            retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
        )
        return AsyncRedis(connection_pool=pool)
