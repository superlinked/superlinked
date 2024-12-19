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

from superlinked.framework.common.dag.context import ContextValue
from superlinked.framework.dsl.app.in_memory.in_memory_app import InMemoryApp
from superlinked.framework.dsl.executor.interactive.interactive_executor import (
    InteractiveExecutor,
)
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.storage.in_memory_vector_database import (
    InMemoryVectorDatabase,
)

logger = structlog.getLogger()


class InMemoryExecutor(InteractiveExecutor[InMemorySource]):
    """
    Initialize the InMemoryExecutor.

    The InMemoryExecutor provides an in-memory implementation for executing queries against indexed data.
    It creates optimized vector spaces based on the provided indices
    and allows querying data from in-memory sources.

    Args:
        sources (InMemorySource | Sequence[InMemorySource]): One or more in-memory data sources to query against.
            Can be a single source or sequence of sources.
        indices (Index | Sequence[Index]): One or more indices that define the vector spaces.
            Can be a single index or sequence of indices.
        context_data (Mapping[str, Mapping[str, ContextValue]] | None, optional): Additional context data
            for execution. The outer mapping key represents the context name, inner mapping contains
            key-value pairs for that context. Defaults to None.
    """

    def __init__(
        self,
        sources: InMemorySource | Sequence[InMemorySource],
        indices: Index | Sequence[Index],
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ) -> None:
        """
        Initialize the InMemoryExecutor.

        The InMemoryExecutor provides an in-memory implementation for executing queries against indexed data.
        It creates optimized vector spaces based on the provided indices
        and allows querying data from in-memory sources.

        Args:
            sources (InMemorySource | Sequence[InMemorySource]): One or more in-memory data sources to query against.
                Can be a single source or sequence of sources.
            indices (Index | Sequence[Index]): One or more indices that define the vector spaces.
                Can be a single index or sequence of indices.
            context_data (Mapping[str, Mapping[str, ContextValue]] | None, optional): Additional context data
                for execution. The outer mapping key represents the context name, inner mapping contains
                key-value pairs for that context. Defaults to None.
        """
        super().__init__(sources, indices, InMemoryVectorDatabase(), context_data)

    def run(self) -> InMemoryApp:
        """
        Run the InMemoryExecutor. It returns an app that can accept queries.
        Returns:
            InMemoryApp: An instance of InMemoryApp.
        """
        app = InMemoryApp(self._sources, self._indices, self._vector_database, self._context)
        self._logger.info("started in-memory app")
        return app
