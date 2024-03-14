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

from abc import ABC, abstractmethod
from typing import Annotated, Generic, TypeVar, get_args

from beartype.typing import Sequence
from typing_extensions import Self

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.util.time_util import now
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.source.source import SourceT
from superlinked.framework.storage.entity_store import EntityStore
from superlinked.framework.storage.entity_store_manager import EntityStoreManager
from superlinked.framework.storage.object_store import ObjectStore
from superlinked.framework.storage.object_store_manager import ObjectStoreManager

ExecutorT = TypeVar("ExecutorT", bound="Executor")


class App(ABC, Generic[ExecutorT]):
    """
    Abstract base class for an App, a running executor that can for example do queries or ingest data.
    """

    def __init__(
        self, executor: ExecutorT, entity_store: EntityStore, object_store: ObjectStore
    ) -> None:
        """
        Initialize the App.

        Args:
            executor (TExecutor): The executor instance.
            entity_store (EntityStore): The entity store instance.
            object_store (ObjectStore): The object store instance.
        """
        self._executor = executor
        self._entity_store = entity_store
        self._entity_store_manager = EntityStoreManager(self._entity_store)
        self._object_store = object_store
        self._object_store_manager = ObjectStoreManager(self._object_store)
        self.now = now()

    @property
    def executor(self) -> ExecutorT:
        """
        Get the executor.

        Returns:
            ExecutorT: The executor instance.
        """
        return self._executor

    @property
    def object_store_manager(self) -> ObjectStoreManager:
        """
        Get the object store manager.

        Returns:
            ObjectStoreManager: The object store manager instance.
        """
        return self._object_store_manager

    @property
    def entity_store_manager(self) -> EntityStoreManager:
        """
        Get the entity store manager.

        Returns:
            EntityStoreManager: The entity store manager instance.
        """
        return self._entity_store_manager


class Executor(ABC, Generic[SourceT]):
    """
    Abstract base class for an executor.
    """

    @TypeValidator.wrap
    def __init__(
        self,
        sources: Sequence[SourceT],
        indices: Annotated[Sequence[Index], TypeValidator.list_validator(Index)],
        context: ExecutionContext,
    ) -> None:
        """
        Initialize the Executor.

        Args:
            sources (list[SourceT]): The list of sources.
            indices (list[Index]): The list of indices.
            context (Mapping[str, Mapping[str, Any]]): The context mapping.
        """
        TypeValidator.validate_list_item_type(
            sources, self.__get_generic_type(), "sources"
        )
        self._sources = sources
        self._indices = indices
        self._context = context

    def __get_generic_type(self) -> type[SourceT]:
        return get_args(self.__class__.__orig_bases__[0])[0]  # type: ignore[attr-defined] # pylint: disable=no-member

    @property
    def context(self) -> ExecutionContext:
        """
        Get the context.

        Returns:
            Mapping[str, Mapping[str, Any]]: The context mapping.
        """
        return self._context

    @abstractmethod
    def run(self) -> App[Self]:
        """
        Abstract method to run the executor.

        Returns:
            App[Self]: An instance of App.
        """
