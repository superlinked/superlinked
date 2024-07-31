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

import logging

from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.storage.in_memory.in_memory_vdb import InMemoryVDB

from executor.app.service.file_object_serializer import FileObjectSerializer

logger = logging.getLogger(__name__)


class PersistenceService:
    def __init__(self, serializer: FileObjectSerializer) -> None:
        self._in_memory_vector_databases: list[InMemoryVDB] = []
        self._serializer = serializer

    def register(self, vdb_connector: VDBConnector) -> None:
        if not isinstance(vdb_connector, InMemoryVDB):
            return
        if vdb_connector in self._in_memory_vector_databases:
            logger.warning("In memory VDB already exists: %s", vdb_connector)
            return
        self._in_memory_vector_databases.append(vdb_connector)

    def persist(self) -> None:
        for vector_database in self._in_memory_vector_databases:
            vector_database.persist(self._serializer)

    def restore(self) -> None:
        for vector_database in self._in_memory_vector_databases:
            vector_database.restore(self._serializer)
