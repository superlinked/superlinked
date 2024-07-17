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


from beartype.typing import Sequence

from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.app.app import App
from superlinked.framework.dsl.app.in_memory.in_memory_app import InMemoryApp
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryExecutor,
)
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestEndpointConfiguration,
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_handler import RestHandler
from superlinked.framework.dsl.source.data_loader_source import DataLoaderSource
from superlinked.framework.dsl.source.rest_source import RestSource


class RestApp(App[RestSource | DataLoaderSource]):
    """
    Rest implementation of the App class.
    """

    def __init__(
        self,
        sources: Sequence[RestSource | DataLoaderSource],
        queries: Sequence[RestQuery],
        endpoint_configuration: RestEndpointConfiguration,
        online_executor: InMemoryExecutor,
    ):
        """
        Initialize the RestApp from a RestExecutor.

        Args:
            sources (Sequence[RestSource | DataLoaderSource]): The list of sources, which can be either
                RestSource or DataLoaderSource.
            queries (Sequence[RestQuery]): The list of queries to be executed by the RestApp.
            endpoint_configuration (RestEndpointConfiguration): The configuration for the REST endpoints.
            online_executor (InMemoryExecutor): The in-memory executor that will be used to run the app.
        """
        self.__online_app = online_executor.run()
        super().__init__(
            sources,
            self.online_app._indices,
            self.online_app._vector_database,
            self.online_app._context,
        )
        self._init_search_indices()
        self._endpoint_configuration = endpoint_configuration
        self._queries = queries

        self.__data_loader_sources = [
            source for source in self._sources if isinstance(source, DataLoaderSource)
        ]

        self.__rest_handler = RestHandler(
            self.__online_app,
            [source for source in self._sources if isinstance(source, RestSource)],
            self._queries,
            self._endpoint_configuration,
        )

    def _init_storage_manager(self) -> StorageManager:
        return StorageManager(self._vector_database._vdb_connector)

    @property
    def data_loader_sources(self) -> Sequence[DataLoaderSource]:
        """
        Property that returns the list of DataLoaderSource instances associated with the RestApp.

        Returns:
            Sequence[DataLoaderSource]: A sequence of DataLoaderSource instances.
        """
        return self.__data_loader_sources

    @property
    def online_app(self) -> InMemoryApp:
        """
        Property that returns the InMemoryApp instance associated with the RestApp.

        Returns:
            InMemoryApp: An instance of InMemoryApp.
        """
        return self.__online_app

    @property
    def handler(self) -> RestHandler:
        """
        Property that returns the RestHandler instance associated with the RestApp.

        Returns:
            RestHandler: An instance of RestHandler.
        """
        return self.__rest_handler
