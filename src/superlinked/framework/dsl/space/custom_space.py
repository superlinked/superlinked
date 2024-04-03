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


from typing import cast

from typing_extensions import override

from superlinked.framework.common.dag.custom_node import CustomNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidSchemaException
from superlinked.framework.common.schema.schema_object import (
    Array,
    SchemaField,
    SchemaObject,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet


class CustomSpace(Space):
    """
    CustomSpace is the instrument of ingesting your own vectors into Superlinked.
    This way you can use your own vectors right away. What you need to know: (you can use numbering too)
    - vectors need to have the same length
    - vectors will be L2 normalised to ensure weighting makes sense
    - weighting can be performed (query-time)
    - you are going to need an Array typed SchemaField to supply your data
    - the Array field will be able to parse any Sequence[float]
    """

    def __init__(
        self,
        vector: Array | list[Array],
        length: int,
    ) -> None:
        """
        Initialize the CustomSpace.

        Args:
            vector (Array | list[Array]): The input containing the vectors
            length (int): The length of inputs (should be the same for all inputs)
        """
        super().__init__(vector, Array)
        unchecked_custom_node_map = {
            vector: CustomNode(
                parent=SchemaFieldNode(vector),
                length=length,
            )
            for vector in self._field_set
        }
        self.vector = SpaceFieldSet(self, cast(set[SchemaField], self._field_set))
        self.__schema_node_map: dict[SchemaObject, CustomNode] = {
            schema_field.schema_obj: node
            for schema_field, node in unchecked_custom_node_map.items()
        }

    @override
    def _get_node(self, schema: SchemaObject) -> Node[Vector]:
        if node := self.__schema_node_map.get(schema):
            return node
        raise InvalidSchemaException(
            f"There's no node corresponding to this schema: {schema._schema_name}"
        )

    @override
    def _get_all_leaf_nodes(self) -> set[Node[Vector]]:
        return set(self.__schema_node_map.values())
