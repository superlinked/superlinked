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
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.app.app import App
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.query_mixin import QueryMixin
from superlinked.framework.dsl.source.source import SourceT
from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.evaluator.online_dag_evaluator import OnlineDagEvaluator
from superlinked.framework.online.source.online_data_processor import (
    OnlineDataProcessor,
)
from superlinked.framework.online.source.online_object_writer import OnlineObjectWriter
from superlinked.framework.online.source.online_source import OnlineSource


@TypeValidator.wrap
class OnlineApp(App[SourceT], QueryMixin):
    """
    Manages the execution environment for online sources and indices.

    This class extends the base App class and incorporates the QueryMixin to handle
    query execution. It is designed to work with online sources and indices, providing
    the necessary setup and management for efficient data processing and querying.
    """

    def __init__(
        self,
        sources: Sequence[SourceT],
        indices: Sequence[Index],
        vector_database: VectorDatabase,
        context: ExecutionContext,
    ) -> None:
        """
        Initialize the OnlineApp with the given sources, indices, vector database, and execution context.

        Args:
            sources (Sequence[SourceT]): A sequence of data sources to be used by the application.
            indices (Sequence[Index]): A sequence of indices for data retrieval and storage.
            vector_database (VectorDatabase): The vector database instance for managing vector data.
            context (ExecutionContext): The execution context providing necessary runtime information.
        """
        super().__init__(sources, indices, vector_database, context)
        self._data_processors: list[OnlineDataProcessor] = []

        self.setup_query_execution(self._indices, self.storage_manager)
        self._init_search_indices()
        self.__setup_sources()

    def __setup_sources(self) -> None:
        """
        Set up the execution environment by initializing data processors and object writers.
        """
        self._data_processors = [
            self._create_data_processor(index) for index in self._indices
        ]
        for data_processor, index in zip(self._data_processors, self._indices):
            for source in self.__filter_index_sources(index):
                source.register(data_processor)
        self._register_object_writer()

    def _create_data_processor(self, index: Index) -> OnlineDataProcessor:
        return OnlineDataProcessor(
            OnlineDagEvaluator(
                index._dag,
                set(index._space_schemas).union(index._effect_schemas),
                self.storage_manager,
            ),
            self.storage_manager,
            self._context,
            index,
        )

    def _register_object_writer(self) -> None:
        object_writer = OnlineObjectWriter(self.storage_manager)
        for source in self._sources:
            if isinstance(source._source, OnlineSource):
                source._source.register(object_writer)

    def _init_storage_manager(self) -> StorageManager:
        return StorageManager(self._vector_database._vdb_connector)

    def __filter_index_sources(self, index: Index) -> Sequence[OnlineSource]:
        return [
            source._source
            for source in self._sources
            if isinstance(source._source, OnlineSource)
            and index.has_schema(source._source._schema)
        ]
