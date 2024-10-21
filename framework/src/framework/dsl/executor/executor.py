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
from typing_extensions import Annotated

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.app.app import App
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.types import SourceT
from superlinked.framework.dsl.storage.vector_database import VectorDatabase


class Executor(ABC, Generic[SourceT]):
    """
    Abstract base class for an executor.
    """

    @TypeValidator.wrap
    def __init__(
        self,
        sources: Sequence[SourceT],
        indices: Annotated[Sequence[Index], TypeValidator.list_validator(Index)],
        vector_database: VectorDatabase,
        context: ExecutionContext,
    ) -> None:
        """
        Initialize the Executor.
        Args:
            sources (list[SourceT]): The list of sources.
            indices (list[Index]): The list of indices.
            vector_database (VectorDatabase): The vector database which the executor will use.
            context (Mapping[str, Mapping[str, Any]]): The context mapping.
        """
        TypeValidator.validate_list_item_type(
            sources, GenericClassUtil.get_single_generic_type(self), "sources"
        )
        self._sources = sources
        self._indices = indices
        self._vector_database = vector_database
        self._context = context

    @abstractmethod
    def run(self) -> App:
        """
        Abstract method to run the executor.
        Returns:
            App: An instance of App.
        """

    def _prohibit_bytes_input(self) -> None:
        for source in self._sources:
            source.parser.set_allow_bytes_input(False)
