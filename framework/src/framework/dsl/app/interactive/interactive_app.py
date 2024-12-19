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
from superlinked.framework.dsl.app.online.online_app import OnlineApp
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.interactive_source import InteractiveSource
from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.queue.no_op_queue.no_op_queue import NoOpQueue


@TypeValidator.wrap
class InteractiveApp(OnlineApp[InteractiveSource]):
    """
    Interactive implementation of the App class.
    """

    def __init__(
        self,
        sources: Sequence[InteractiveSource],
        indices: Sequence[Index],
        vector_database: VectorDatabase,
        context: ExecutionContext,
        init_search_indices: bool = True,
    ) -> None:
        """
        Initialize the InteractiveApp from an InteractiveExecutor.
        Args:
            sources (list[InteractiveSource]): List of interactive sources.
            indices (list[Index]): List of indices.
            vector_database (VectorDatabase | None): Vector database instance. Defaults to InMemory.
            context (Mapping[str, Mapping[str, Any]]): Context mapping.
            init_search_indices (bool): Decides if the search indices need to be created. Defaults to True.
        """
        super().__init__(sources, indices, vector_database, context, init_search_indices, NoOpQueue())
        self._allow_data_ingestion_for_sources(sources)

    def _allow_data_ingestion_for_sources(self, sources: Sequence[InteractiveSource]) -> None:
        for source in sources:
            source.allow_data_ingestion()
