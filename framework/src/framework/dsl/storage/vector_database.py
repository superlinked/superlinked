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

from beartype.typing import Generic, TypeVar

from superlinked.framework.common.storage.vdb_connector import VDBConnector

VDBConnectorT = TypeVar("VDBConnectorT", bound=VDBConnector)


class VectorDatabase(ABC, Generic[VDBConnectorT]):
    """
    Abstract base class for a Vector Database.

    This class serves as a blueprint for vector databases, ensuring that any concrete implementation
    provides a connector to the vector database.

    Attributes:
        _vdb_connector (VDBConnectorT): An abstract property that should return an instance of a VDBConnector.
    """

    @property
    @abstractmethod
    def _vdb_connector(self) -> VDBConnectorT:
        """
        Abstract property to get the vector database connector.

        Returns:
            VDBConnectorT: An instance of a VDBConnector.
        """
