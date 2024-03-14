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

import uuid
from abc import ABC
from typing import Generic, TypeVar

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.persistence_params import PersistenceParams
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage.persistence_type import PersistenceType

# NodeDataType
NDT = TypeVar("NDT")
# NodeType
NT = TypeVar("NT", bound="Node")


class Node(Generic[NDT], ABC):
    def __init__(
        self,
        parents: list[Node],
        schemas: set[SchemaObject] | None = None,
        dag_effects: set[DagEffect] | None = None,
        persistence_params: PersistenceParams | None = None,
    ) -> None:
        self.children: list[Node] = []
        self.parents = parents
        self._node_id = (
            f"{self.class_name}-{str(uuid.uuid4())}"
            f'({"|".join([parent.node_id for parent in self.parents])})'
        )
        self.schemas: set[SchemaObject] = (schemas or set()).union(
            {schema for parent in parents for schema in parent.schemas}
            if parents
            else set()
        )
        self.dag_effects: set[DagEffect] = (dag_effects or set()).union(
            {dag_effect for parent in parents for dag_effect in parent.dag_effects}
            if parents
            else set()
        )
        self._persistence_params = persistence_params or PersistenceParams()
        for parent in self.parents:
            parent._append_child(self)

    def _append_child(self, child: Node) -> None:
        self.children.append(child)
        self._persistence_params.persist_evaluation_result |= (
            child._persistence_params.persist_parent_evaluation_result
        )

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def persist_evaluation_result(self) -> bool:
        return self._persistence_params.persist_evaluation_result

    @property
    def persistence_type(self) -> PersistenceType:
        return self._persistence_params.persistence_type

    def project_parents_to_schema(self, schema: SchemaObject) -> list[Node]:
        if schema in self.schemas:
            return [parent for parent in self.parents if schema in parent.schemas]
        return []

    def project_parents_for_dag_effect(self, dag_effect: DagEffect) -> list[Node]:
        if dag_effect in self.dag_effects:
            return [
                parent for parent in self.parents if dag_effect in parent.dag_effects
            ]
        return []
