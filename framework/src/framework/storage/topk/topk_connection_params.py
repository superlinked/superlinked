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


from superlinked.framework.common.exception import FeatureNotSupportedException
from superlinked.framework.storage.common.connection_params import ConnectionParams


class TopKConnectionParams(ConnectionParams):
    def __init__(
        self,
        api_key: str,
        region: str,
        https: bool,
        host: str,
    ) -> None:
        super().__init__()
        self._api_key = api_key
        self._region = region
        self._https = https
        self._host = host

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def region(self) -> str:
        return self._region

    @property
    def https(self) -> bool:
        return self._https

    @property
    def host(self) -> str:
        return self._host

    @property
    def connection_string(self) -> str:
        raise FeatureNotSupportedException("TopK does not support connection strings")
