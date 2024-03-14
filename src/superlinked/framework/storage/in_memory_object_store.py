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

from __future__ import annotations

from superlinked.framework.common.data_types import Json
from superlinked.framework.storage.object_store import ObjectStore


class InMemoryObjectStore(ObjectStore[Json]):
    def __init__(self) -> None:
        self.__store: dict[str, Json] = {}

    def save(self, row_id: str, data: Json) -> None:
        self.__store[row_id] = data

    def load(self, row_id: str) -> Json | None:
        return self.__store.get(row_id)

    def load_all(self) -> list[Json]:
        return list(self.__store.values())
