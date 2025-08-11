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

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_dag import SchemaDag
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject


class Dag:
    def __init__(self, nodes: list[Node], dag_effects: set[DagEffect] | None = None) -> None:
        self.nodes = nodes
        self._index_node = self.__init_index_node(self.nodes)
        self.__check_for_node_id_duplication()
        self.dag_effects = dag_effects or set()
        node_id_schema_map: dict[str, set[IdSchemaObject]] = self.__init_node_id_schema_map(self.nodes)
        self.__schemas: set[IdSchemaObject] = self.__init_schemas(node_id_schema_map)
        self.__schema_dag_map: dict[IdSchemaObject, SchemaDag] = self.__init_schema_schema_dag_map(
            self.__schemas, node_id_schema_map
        )

    @property
    def schemas(self) -> set[IdSchemaObject]:
        return self.__schemas

    @property
    def index_node(self) -> IndexNode:
        return self._index_node

    def project_to_schema(self, schema: IdSchemaObject) -> SchemaDag:
        if (dag := self.__schema_dag_map.get(schema)) is not None:
            return dag
        raise InvalidStateException(f"SchemaDag for the given schema ({schema._base_class_name}) doesn't exist.")

    def __init_index_node(self, nodes: Sequence[Node]) -> IndexNode:
        if index_node := next((node for node in nodes if isinstance(node, IndexNode)), None):
            return index_node
        raise InvalidStateException(f"{type(self).__name__} doesn't have an IndexNode.")

    def __init_node_id_schema_map(self, nodes: list[Node]) -> dict[str, set[IdSchemaObject]]:
        return {node.node_id: node.schemas for node in nodes}

    def __init_schemas(self, node_id_schema_map: dict[str, set[IdSchemaObject]]) -> set[IdSchemaObject]:
        return {schema for schemas in node_id_schema_map.values() for schema in schemas}

    def __init_schema_schema_dag_map(
        self,
        schemas: set[IdSchemaObject],
        node_id_schema_map: dict[str, set[IdSchemaObject]],
    ) -> dict[IdSchemaObject, SchemaDag]:
        return {schema: self.__project_to_schema(schema, node_id_schema_map) for schema in schemas}

    def __project_to_schema(
        self, schema: IdSchemaObject, node_id_schema_map: dict[str, set[IdSchemaObject]]
    ) -> SchemaDag:
        filtered_nodes = {node for node in self.nodes if schema in node_id_schema_map[node.node_id]}
        projected_parents = set(parent for node in filtered_nodes for parent in node.project_parents_to_schema(schema))
        return SchemaDag(
            schema,
            list(projected_parents.union(filtered_nodes)),
        )

    def __check_for_node_id_duplication(self) -> None:
        node_ids = set()
        for node in self.nodes:
            if node.node_id in node_ids:
                raise InvalidStateException(
                    "Node id is duplicated.", node_id=node.node_id, node_type=type(node).__name__
                )
            node_ids.add(node._node_id)
