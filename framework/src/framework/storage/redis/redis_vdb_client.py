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

import time

from redis import Redis

CONNECTION_REFRESH_INTERVAL_SECONDS = 1800


class RedisVDBClient:
    """A Redis client wrapper that automatically refreshes the connection when needed."""

    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self._last_activity_time = time.time()
        self.__client = self._create_client()

    @property
    def client(self) -> Redis:
        """
        Property to access the Redis client with connection refresh.
        """
        self._refresh_connection_if_needed()
        return self.__client

    def _create_client(self) -> Redis:
        return Redis.from_url(self._connection_string, protocol=3)

    def _refresh_connection_if_needed(self) -> None:
        current_time = time.time()
        if current_time - self._last_activity_time > CONNECTION_REFRESH_INTERVAL_SECONDS:
            self.__client.close()
            self.__client = self._create_client()
        self._last_activity_time = current_time
