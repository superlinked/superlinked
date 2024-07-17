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

from beartype.typing import Generic, Sequence

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.storage_manager.storage_manager import (
    SearchIndexParams,
    StorageManager,
)
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.source import SourceT
from superlinked.framework.dsl.storage.vector_database import VectorDatabase


class App(ABC, Generic[SourceT]):
    """
    Abstract base class for an App, a running executor that can, for example, do queries or ingest data.
    """

    def __init__(
        self,
        sources: Sequence[SourceT],
        indices: Sequence[Index],
        vector_database: VectorDatabase,
        context: ExecutionContext,
    ) -> None:
        """
        Initialize the App.
        Args:
            sources (list[SourceT]): The list of sources.
            indices (list[Index]): The list of indices.
            vector_database (VectorDatabase): The vector database which the executor will use.
            context (Mapping[str, Mapping[str, Any]]): The context mapping.
        """
        self._sources = sources
        self._indices = indices
        self._vector_database = vector_database
        self._context = context
        self._storage_manager = self._init_storage_manager()
        self.now = context.now()

    @property
    def storage_manager(self) -> StorageManager:
        """
        Get the storage manager.
        Returns:
            StorageManager: The storage manager instance.
        """
        return self._storage_manager

    @abstractmethod
    def _init_storage_manager(self) -> StorageManager:
        pass

    def _init_search_indices(self) -> None:
        search_index_params = [
            SearchIndexParams(
                index._dag.index_node.node_id,
                index._dag.index_node.length,
                index._fields,
            )
            for index in self._indices
        ]
        self.storage_manager.init_search_indices(search_index_params)
