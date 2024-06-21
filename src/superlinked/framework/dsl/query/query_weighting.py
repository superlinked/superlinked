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

from superlinked.framework.common.dag.concatenation_node import ConcatenationNode
from superlinked.framework.common.dag.context import SPACE_WEIGHT_PARAM_NAME
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.exception import InvalidSchemaException
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaObject

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryWeighting"] = False


class QueryWeighting:
    def __init__(self, dag: Dag) -> None:
        self.__node_id_weighable_node_id_map = self._init_weighable_node_map(dag)

    def get_node_weights(
        self, node_id_weight_map: dict[str, float]
    ) -> dict[str, dict[str, float]]:
        return {
            self.get_weighable_node_id(node_id): {SPACE_WEIGHT_PARAM_NAME: weight}
            for node_id, weight in node_id_weight_map.items()
        }

    def get_weighable_node_id(self, node_id: str) -> str:
        return self.__node_id_weighable_node_id_map.get(node_id, node_id)

    def _init_weighable_node_map(self, dag: Dag) -> dict[str, str]:
        concatenation_nodes_with_schema = self._get_concatenation_nodes_with_schema(
            dag.nodes
        )
        return {
            ancestor.node_id: cn_parent.node_id
            for cn, schema_ in concatenation_nodes_with_schema
            for cn_parent in cn.parents
            for ancestor in self._get_ancestors_by_schema(cn_parent, schema_)
        }

    def _get_concatenation_nodes_with_schema(
        self,
        nodes: list[Node],
    ) -> list[tuple[ConcatenationNode, SchemaObject]]:
        return [
            self._get_concatenation_node_with_schema(node)
            for node in nodes
            if isinstance(node, ConcatenationNode)
        ]

    def _get_concatenation_node_with_schema(
        self, concatenation_node: ConcatenationNode
    ) -> tuple[ConcatenationNode, SchemaObject]:
        item_schemas = [
            schema_
            for schema_ in concatenation_node.schemas
            if not isinstance(schema_, EventSchemaObject)
        ]
        if len(item_schemas) != 1:
            raise InvalidSchemaException(
                "ConcatenationNode must have exactly 1 non-event type schemas."
            )
        return (concatenation_node, item_schemas[0])

    def _get_ancestors_by_schema(self, node: Node, schema_: SchemaObject) -> set[Node]:
        return {
            parent_ancestor
            for parent in node.parents
            if schema_ in parent.schemas
            for parent_ancestor in self._get_ancestors_by_schema(parent, schema_)
        }
