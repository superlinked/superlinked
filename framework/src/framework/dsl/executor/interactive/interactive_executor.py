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
from beartype.typing import Generic, Mapping, Sequence, TypeVar

from superlinked.framework.common.dag.context import (
    ContextValue,
    ExecutionContext,
    ExecutionEnvironment,
)
from superlinked.framework.dsl.app.interactive.interactive_app import InteractiveApp
from superlinked.framework.dsl.executor.executor import Executor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.interactive_source import InteractiveSource
from superlinked.framework.dsl.storage.in_memory_vector_database import (
    InMemoryVectorDatabase,
)
from superlinked.framework.dsl.storage.vector_database import VectorDatabase

logger = structlog.getLogger()

InteractiveSourceT = TypeVar("InteractiveSourceT", bound=InteractiveSource)


class InteractiveExecutor(Executor[InteractiveSourceT], Generic[InteractiveSourceT]):
    """
    Interactive implementation of the Executor class. Supply it with the sources through which
    your data is received, the indices indicating the desired vector spaces, and optionally a vector database.
    The executor will create the spaces optimized for search.
    """

    def __init__(
        self,
        sources: InteractiveSourceT | Sequence[InteractiveSourceT],
        indices: Index | Sequence[Index],
        vector_database: VectorDatabase | None = None,
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ) -> None:
        """
        Initialize the InteractiveExecutor.
        Args:
            sources (list[InteractiveSourceT]): List of interactive sources.
            indices (list[Index]): List of indices.
            vector_database: (VectorDatabase | None): Vector database instance. Defaults to InMemoryVectorDatabase.
            context_data (Mapping[str, Mapping[str, ContextValue]] | None):
                Context data for execution. Defaults to None.
        """
        super().__init__(
            sources,
            indices,
            vector_database or InMemoryVectorDatabase(),
            ExecutionContext.from_context_data(context_data, environment=ExecutionEnvironment.IN_MEMORY),
        )
        self._logger = logger.bind(
            source_schemas=[source._schema._schema_name for source in self._sources],
            index_node_ids=[index._node.node_id for index in self._indices],
        )

    def run(self) -> InteractiveApp:
        """
        Run the InteractiveExecutor. It returns an app that can accept queries.
        Returns:
            InteractiveApp: An instance of InteractiveApp.
        """
        app = InteractiveApp(self._sources, self._indices, self._vector_database, self._context)
        self._logger.info("started interactive app")
        return app
