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

import sys

from superlinked.evaluation.storage_usage.exception import UnsupportedVDBException
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.storage.in_memory.in_memory_vdb import InMemoryVDB
from superlinked.framework.storage.qdrant.qdrant_vdb_connector import QdrantVDBConnector


class VDBWatcher:
    def __init__(self, vdb_connector: VDBConnector) -> None:
        self.__vdb_connector = vdb_connector

    # If needed implement this as part of the vdb interface.
    def get_memory_usage(self) -> int:
        if isinstance(self.__vdb_connector, InMemoryVDB):
            return sys.getsizeof(self.__vdb_connector._vdb)
        if isinstance(self.__vdb_connector, QdrantVDBConnector):
            snapshot = self.__vdb_connector._client.create_full_snapshot()
            name, size = (snapshot.name, snapshot.size) if snapshot is not None else (None, 0)
            if name is not None:
                self.__vdb_connector._client.delete_full_snapshot(name)
            return size
        raise UnsupportedVDBException(f"Checking memory usage of {type(self.__vdb_connector)} is not yet implemented")
