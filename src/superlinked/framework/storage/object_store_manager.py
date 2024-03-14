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

from dataclasses import dataclass
from typing import Generic

from superlinked.framework.storage.object_store import ObjectStore, ObjectTypeT


@dataclass
class DataId:
    schema_id: str
    object_id: str

    def __str__(self) -> str:
        return f"{self.schema_id}:{self.object_id}"


class ObjectStoreManager(Generic[ObjectTypeT]):
    def __init__(self, store: ObjectStore[ObjectTypeT]) -> None:
        self.__store = store

    def save(self, data_id: DataId, data: ObjectTypeT) -> None:
        self.__store.save(ObjectStoreManager._get_row_id_from_data_id(data_id), data)

    def load(self, data_id: DataId) -> ObjectTypeT | None:
        return self.__store.load(ObjectStoreManager._get_row_id_from_data_id(data_id))

    def load_all(self) -> list[ObjectTypeT]:
        return self.__store.load_all()

    @staticmethod
    def _get_row_id_from_data_id(data_id: DataId) -> str:
        return f"{data_id.schema_id}:{data_id.object_id}"
