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

import hashlib
from abc import ABC, abstractmethod

from beartype.typing import Any, Generic, Sequence, TypeVar, cast
from typing_extensions import Self

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.persistence_params import PersistenceParams
from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage.persistence_type import PersistenceType
from superlinked.framework.common.util.string_util import StringUtil

NodeDataT = TypeVar("NodeDataT", bound=NodeDataTypes)
# NodeType
NT = TypeVar("NT", bound="Node")


class Node(Generic[NodeDataT], ABC):  # pylint: disable=too-many-instance-attributes #FAI-3022
    _instances: dict[str, Node] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)  # type: ignore
        node_id = instance.node_id
        if node_id in cls._instances:
            return cast(Self, cls._instances[node_id])
        cls._instances[node_id] = instance
        return instance

    def __init__(  # pylint: disable=too-many-arguments #FAI-3022
        self,
        node_data_type: type[NodeDataT],
        parents: Sequence[Node],
        schemas: set[IdSchemaObject] | None = None,
        dag_effects: set[DagEffect] | None = None,
        persistence_params: PersistenceParams | None = None,
        non_nullable_parents: frozenset[Node] | None = None,
    ) -> None:
        self._node_data_type = node_data_type
        self._node_id: str | None = None
        self.children: list[Node] = []
        self.parents = parents
        self.schemas: set[IdSchemaObject] = (schemas or set()).union(
            {schema for parent in parents for schema in parent.schemas} if parents else set()
        )
        self.dag_effects: set[DagEffect] = (dag_effects or set()).union(
            {dag_effect for parent in parents for dag_effect in parent.dag_effects} if parents else set()
        )
        self._persistence_params = persistence_params or PersistenceParams()
        self.non_nullable_parents = non_nullable_parents or frozenset()
        for parent in self.parents:
            parent._append_child(self)

    def _append_child(self, child: Node) -> None:
        self.children.append(child)
        self._persistence_params.persist_node_result |= child._persistence_params.persist_parent_node_result

    @property
    def node_data_type(self) -> type[NodeDataT]:
        return self._node_data_type

    @property
    def node_id(self) -> str:
        if not self._node_id:
            self._node_id = self._generate_node_id()
        return self._node_id

    @property
    def is_root(self) -> bool:
        return len(self.parents) == 0

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def persist_node_result(self) -> bool:
        return self._persistence_params.persist_node_result

    @property
    def persistence_type(self) -> PersistenceType:
        return self._persistence_params.persistence_type

    @abstractmethod
    def _get_node_id_parameters(self) -> dict[str, Any]:
        """
        This method should include all class members that define its functionality, excluding the parent(s).
        """

    def __str__(self) -> str:
        members = StringUtil.sort_and_serialize(self._get_node_id_parameters())
        return f"{self.class_name}({members})"

    def _generate_node_id(self) -> str:
        to_hash = self._calculate_node_id_hash_input()
        return hashlib.sha3_256(to_hash.encode()).hexdigest()[:16]

    def _calculate_node_id_hash_input(self) -> str:
        to_hash = " | ".join(
            [StringUtil.sort_and_serialize(self._get_node_id_parameters())]
            + [parent.node_id for parent in self.parents]
        )
        return to_hash

    def project_parents_to_schema(self, schema: IdSchemaObject) -> Sequence[Node]:
        if schema in self.schemas:
            return [parent for parent in self.parents if schema in parent.schemas]
        return []

    def project_parents_for_dag_effect(self, dag_effect: DagEffect) -> Sequence[Node]:
        if dag_effect in self.dag_effects:
            return [parent for parent in self.parents if dag_effect in parent.dag_effects]
        return []
