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

import structlog
from beartype.typing import Mapping, Sequence

from superlinked.framework.common.dag.context import (
    ContextValue,
    ExecutionContext,
    ExecutionEnvironment,
)
from superlinked.framework.dsl.app.in_memory.in_memory_app import InMemoryApp
from superlinked.framework.dsl.executor.executor import Executor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.storage.in_memory_vector_database import (
    InMemoryVectorDatabase,
)

logger = structlog.getLogger()


class InMemoryExecutor(Executor[InMemorySource]):
    """
    In-memory implementation of the Executor class. Supply it with the sources through which
    your data is received, and the indices indicating the desired vector spaces, and the executor will
    create the spaces optimized for search.
    Attributes:
        sources (list[InMemorySource]): List of in-memory sources.
        indices (list[Index]): List of indices.
        vector_database (VectorDatabase | None): Vector database instance. Defaults to InMemory.
    """

    def __init__(
        self,
        sources: Sequence[InMemorySource],
        indices: Sequence[Index],
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ) -> None:
        """
        Initialize the InMemoryExecutor.
        Args:
            sources (list[InMemorySource]): List of in-memory sources.
            indices (list[Index]): List of indices.
            vector_database: (VectorDatabase | None): Vector database instance. Defaults to InMemory.
            context (Mapping[str, Mapping[str, Any]]): Context mapping.
        """
        super().__init__(
            sources,
            indices,
            InMemoryVectorDatabase(),
            ExecutionContext.from_context_data(
                context_data, environment=ExecutionEnvironment.IN_MEMORY
            ),
        )
        self._logger = logger.bind(
            source_schemas=[source._schema._schema_name for source in sources],
            index_node_ids=[index._node.node_id for index in indices],
        )

    def run(self) -> InMemoryApp:
        """
        Run the InMemoryExecutor. It returns an app that can accept queries.
        Returns:
            InMemoryApp: An instance of InMemoryApp.
        """
        app = InMemoryApp(
            self._sources, self._indices, self._vector_database, self._context
        )
        self._logger.info("started inmemory app")
        return app
