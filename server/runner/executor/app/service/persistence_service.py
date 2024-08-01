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

from executor.app.service.file_object_serializer import FileObjectSerializer

logger = logging.getLogger(__name__)


class PersistenceService:
    def __init__(self, serializer: FileObjectSerializer) -> None:
        self._vdb_connectors: list[VDBConnector] = []
        self._serializer = serializer

    def register(self, vdb_connector: VDBConnector) -> None:
        if vdb_connector in self._vdb_connectors:
            logger.warning("VDB connector already exists: %s", vdb_connector)
            return
        self._vdb_connectors.append(vdb_connector)

    def persist(self) -> None:
        for vdb_connector in self._vdb_connectors:
            vdb_connector.persist(self._serializer)

    def restore(self) -> None:
        for vdb_connector in self._vdb_connectors:
            vdb_connector.restore(self._serializer)
