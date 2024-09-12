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

from beartype.typing import cast

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import (
    LeafNodeCountException,
    LeafNodeTypeException,
    MultipleRootSchemaException,
)
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.exception import SchemaMismatchException
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_index_node import OnlineIndexNode
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.online_schema_field_node import (
    OnlineSchemaFieldNode,
)


class OnlineSchemaDag:
    """
    Represents an `OnlineDag`'s projection to a particular schema.
    Must have exactly one leaf `Node` of type `OnlineIndexNode`.
    """

    def __init__(self, schema: SchemaObject, nodes: list[OnlineNode]) -> None:
        self.__validate(schema, nodes)
        self.__nodes = nodes
        # There's exactly 1 leaf `OnlineNode` as it was already validated.
        self.__leaf_node = cast(
            OnlineIndexNode,
            [node for node in self.__nodes if len(node.children) == 0][0],
        )

    @property
    def nodes(self) -> list[OnlineNode]:
        return self.__nodes

    @property
    def leaf_node(self) -> OnlineIndexNode:
        return self.__leaf_node

    def evaluate(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[Vector]]:
        return self.leaf_node.evaluate_next(parsed_schemas, context)

    def __validate(self, schema: SchemaObject, nodes: list[OnlineNode]) -> None:
        class_name = self.__class__.__name__
        leaf_nodes = [node for node in nodes if len(node.children) == 0]
        if len(leaf_nodes) != 1:
            raise LeafNodeCountException(
                f"{class_name} must have exactly one leaf Node."
            )
        if not isinstance(leaf_nodes[0], OnlineIndexNode):
            raise LeafNodeTypeException(
                f"{class_name} must have a OnlineIndexNode leaf Node."
            )
        root_node_schemas = set(
            cast(SchemaFieldNode, node.node).schema_field.schema_obj
            for node in nodes
            if isinstance(node, OnlineSchemaFieldNode)
        )
        if len(root_node_schemas) != 1:
            raise MultipleRootSchemaException(
                f"{class_name}'s nodes must have the same root schema."
            )
        if schema not in root_node_schemas:
            raise SchemaMismatchException(
                (
                    f"{class_name} was instantiated with a schema object different from the nodes' root schema ",
                    f"object: {schema.__class__.__name__} <> {list(root_node_schemas)[0]._base_class_name}.",
                )
            )
