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

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.app.interactive.interactive_app import InteractiveApp
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.storage.in_memory_vector_database import (
    InMemoryVectorDatabase,
)
from superlinked.framework.dsl.storage.vector_database import VectorDatabase


@TypeValidator.wrap
class InMemoryApp(InteractiveApp):
    """
    In-memory implementation of the App class.
    """

    def __init__(
        self,
        sources: Sequence[InMemorySource],
        indices: Sequence[Index],
        vector_database: VectorDatabase | None,
        context: ExecutionContext,
    ) -> None:
        """
        Initialize the InMemoryApp from an InMemoryExecutor.
        Args:
            sources (list[InMemorySource]): List of in-memory sources.
            indices (list[Index]): List of indices.
            vector_database (VectorDatabase | None): Vector database instance. Defaults to InMemory.
            context (Mapping[str, Mapping[str, Any]]): Context mapping.
        """
        super().__init__(sources, indices, vector_database or InMemoryVectorDatabase(), context)
