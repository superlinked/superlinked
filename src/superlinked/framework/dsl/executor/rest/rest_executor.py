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

from typing import Mapping

from superlinked.framework.common.dag.context import ContextValue
from superlinked.framework.dsl.executor.executor import App, Executor
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryExecutor,
)
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestEndpointConfiguration,
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_handler import RestHandler
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.rest_source import RestSource


class RestExecutor(Executor[RestSource]):
    """
    The RestExecutor is a subclass of the Executor base class. It encapsulates all the parameters required for
    the REST application. It also instantiates an InMemoryExecutor for data storage purposes.

    Attributes:
        sources (list[RestSource]): List of Rest sources that has information about the schema.
        indices (list[Index]): List indices.
        queries (list[RestQuery]): List of executable queries.
        endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.
    """

    def __init__(
        self,
        sources: list[RestSource],
        indices: list[Index],
        queries: list[RestQuery],
        endpoint_configuration: RestEndpointConfiguration | None = None,
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ):
        """
        Initialize the RestExecutor.

        Attributes:
            sources (list[RestSource]): List of Rest sources that has information about the schema.
            indices (list[Index]): List indices.
            queries (list[RestQuery]): List of executable queries.
            endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.
        """
        online_sources = [source._online_source for source in sources]
        self._online_executor = InMemoryExecutor(online_sources, indices, context_data)
        super().__init__(sources, indices, self._online_executor.context)

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
        super().__init__(
            executor, self.__online_app._entity_store, self.__online_app._object_store
        )

        self.__rest_handler = RestHandler(
            self.__online_app,
            executor._sources,
            executor._queries,
            executor._endpoint_configuration,
        )

    @property
    def handler(self) -> RestHandler:
        """
        Property that returns the RestHandler instance associated with the RestApp.

        Returns:
            RestHandler: An instance of RestHandler.
        """
        return self.__rest_handler
