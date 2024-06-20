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

from superlinked.framework.storage.common.connection_params import ConnectionParams

URL_PREFIX = "redis://"


class RedisConnectionParams(ConnectionParams):
    def __init__(self, host: str, port: int, **extra_params: Any) -> None:
        super().__init__()
        extra_params_str = self.get_uri_params_string(**extra_params)
        self._connection_string = f"{URL_PREFIX}{host}:{port}{extra_params_str}"

    @property
    def connection_string(self) -> str:
        return self._connection_string
