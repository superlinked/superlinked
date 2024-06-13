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

from typing import Mapping, Sequence

from superlinked.framework.common.dag.context import ContextValue
from superlinked.framework.dsl.executor.executor import App, Executor
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryApp,
    InMemoryExecutor,
)
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestEndpointConfiguration,
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_handler import RestHandler
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.data_loader_source import DataLoaderSource
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.storage.vector_database import VectorDatabase


class RestExecutor(Executor[RestSource | DataLoaderSource]):
    """
    The RestExecutor is a subclass of the Executor base class. It encapsulates all the parameters required for
    the REST application. It also instantiates an InMemoryExecutor for data storage purposes.

    Attributes:
        sources (Sequence[RestSource]): A sequence of rest sources that has information about the schema.
        indices (Sequence[Index]): A sequence of indices.
        queries (Sequence[RestQuery]): A sequence of executable queries.
        endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        sources: Sequence[RestSource | DataLoaderSource],
        indices: Sequence[Index],
        queries: Sequence[RestQuery],
        vector_database: VectorDatabase,
        endpoint_configuration: RestEndpointConfiguration | None = None,
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ):
        """
        Initialize the RestExecutor.
        Attributes:
            sources (Sequence[RestSource]): A sequence ofRest sources that has information about the schema.
            indices (Sequence[Index]): A sequence of indices.
            queries (Sequence[RestQuery]): A sequence ofexecutable queries.
            vector_database (VectorDatabase): Vector database instance.
            endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.
        """
        online_sources = [source._online_source for source in sources]
        self._online_executor = InMemoryExecutor(
            online_sources, indices, vector_database, context_data
        )
        super().__init__(
            sources, indices, vector_database, self._online_executor.context
        )

        self._queries = queries
        self._endpoint_configuration = (
            endpoint_configuration or RestEndpointConfiguration()
        )

    def run(self) -> RestApp:
        """
        Run the RestExecutor. It returns an app that will create rest endpoints.

        Returns:
            RestApp: An instance of RestApp.
        """
        return RestApp(self)


class RestApp(App):
    """
    Rest implementation of the App class.

    Attributes:
        executor (RestExecutor): An instance of RestExecutor.
    """

    def __init__(self, executor: RestExecutor):
        """
        Initialize the RestApp from an RestExecutor.

        Args:
            executor (RestExecutor): An instance of RestExecutor.
        """
        self.__online_app = executor._online_executor.run()
        super().__init__(executor)

        self.__data_loader_sources = [
            source
            for source in executor._sources
            if isinstance(source, DataLoaderSource)
        ]

        self.__rest_handler = RestHandler(
            self.__online_app,
            [source for source in executor._sources if isinstance(source, RestSource)],
            executor._queries,
            executor._endpoint_configuration,
        )

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
