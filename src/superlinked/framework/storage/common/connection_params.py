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

from abc import ABC, abstractmethod

from beartype.typing import Any


class ConnectionParams(ABC):
    @property
    @abstractmethod
    def connection_string(self) -> str:
        pass

    @staticmethod
    def get_uri_params_string(**params: Any) -> str:
        params_str = "&".join([f"{key}={value}" for key, value in params.items()])
        return "/?" + params_str if params_str else ""
