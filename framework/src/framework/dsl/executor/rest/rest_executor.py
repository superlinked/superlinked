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

from beartype.typing import Any, Mapping, Sequence

from superlinked.framework.blob.blob_handler_factory import (
    BlobHandlerConfig,
    BlobHandlerFactory,
)
from superlinked.framework.common.dag.context import (
    ContextValue,
    ExecutionContext,
    ExecutionEnvironment,
)
from superlinked.framework.dsl.app.rest.rest_app import RestApp
from superlinked.framework.dsl.executor.executor import Executor
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestEndpointConfiguration,
    RestQuery,
)
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.data_loader_source import DataLoaderSource
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.queue.queue_factory import QueueFactory


class RestExecutor(Executor[RestSource | DataLoaderSource]):
    """
    The RestExecutor is a specialized subclass of the Executor base class designed to handle REST applications.
    It encapsulates all necessary parameters for configuring and running a REST-based application.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        sources: Sequence[RestSource | DataLoaderSource],
        indices: Sequence[Index],
        queries: Sequence[RestQuery],
        vector_database: VectorDatabase,
        endpoint_configuration: RestEndpointConfiguration | None = None,
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
        blob_handler_config: BlobHandlerConfig | None = None,
    ):
        """
        Initialize the RestExecutor with the provided parameters.

        Args:
            sources (Sequence[RestSource | DataLoaderSource]): Sources, either RestSource or DataLoaderSource.
            indices (Sequence[Index]): Indices for the RestExecutor.
            queries (Sequence[RestQuery]): Queries to execute.
            vector_database (VectorDatabase): Vector database instance.
            endpoint_configuration (RestEndpointConfiguration | None): REST endpoint configuration. Defaults to None.
            context_data (Mapping[str, Mapping[str, ContextValue]] | None):
                Context data for execution. Defaults to None.
        """
        super().__init__(
            sources,
            indices,
            vector_database,
            ExecutionContext.from_context_data(context_data, environment=ExecutionEnvironment.ONLINE),
        )
        self._prohibit_bytes_input()
        self._queries = queries
        self._endpoint_configuration = endpoint_configuration or RestEndpointConfiguration()
        self._queue = QueueFactory.create_queue(dict[str, Any])
        self._blob_handler = BlobHandlerFactory.create_blob_handler(blob_handler_config)

    def run(self) -> RestApp:
        """
        Run the RestExecutor. It returns an app that will create rest endpoints.

        Returns:
            RestApp: An instance of RestApp.
        """
        return RestApp(
            self._sources,
            self._indices,
            self._queries,
            self._vector_database,
            self._context,
            self._endpoint_configuration,
            self._queue,
            self._blob_handler,
        )
