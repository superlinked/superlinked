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

from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.number_embedding_node import NumberEmbeddingNode
from superlinked.framework.common.dag.number_similarity_node import NumberSimilarityNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.number_embedding import Mode
from superlinked.framework.common.schema.schema_object import Number, SchemaObject
from superlinked.framework.dsl.space.exception import (
    InvalidSpaceParamException,
    NoDefaultNodeException,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet


class NumberSpace(Space):
    """
    NumberSpace is used to encode numerical values within a specified range.
    The range is defined by the min_value and max_value parameters.
    The preference can be controlled by the mode parameter.

    Note: In similar mode you MUST add a similar clause to the query or it will raise.

    Attributes:
        number (SpaceFieldSet): A set of Number objects.
            It is a SchemaFieldObject not regular python ints or floats.
        min_value (float | int): This represents the minimum boundary. Any number lower than
            this will be considered as this minimum value. It can be either a float or an integer.
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
        mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
            Similar mode expects a .similar on the query, otherwise it will default to maximum.
        negative_filter (float): This is a value that will be set for everything that is equal or
            lower than the min_value. It can be a float. It defaults to 0 (No effect)

    Raises:
        InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
            Or the min_value is bigger than the max value, or the negative filter bigger than 0
        InvalidSchemaException: If there's no node corresponding to a given schema.

    """

    def __init__(
        self,
        number: Number | list[Number],
        min_value: float | int,
        max_value: float | int,
        mode: Mode,
        negative_filter: float = 0.0,
    ) -> None:
        """
        Initializes the NumberSpace object.

        Attributes:
            number (SpaceFieldSet): A set of Number objects.
                These are SchemaFieldObjects not regular python ints or floats.
            min_value (float | int): This represents the minimum boundary. Any number lower than
                this will be considered as this minimum value. It can be either a float or an integer.
            max_value (float | int): This represents the maximum boundary. Any number higher than
                this will be considered as this maximum value. It can be either a float or an integer.
            mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
                Similar mode expects a .similar on the query, otherwise it will default to maximum.
            negative_filter (float): This is a value that will be set for everything that is equal or
                lower than the min_value. It can be a float. It defaults to 0 (No effect)

         Raises:
            InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
                Or the min_value is bigger than the max value, or the negative filter bigger than 0
            InvalidSchemaException: If there's no node corresponding to a given schema.
        """
        super().__init__(number, Number)
        self.__validate_parameters(min_value, max_value, negative_filter)
        self.min_value: float = float(min_value)
        self.max_value: float = float(max_value)
        self.mode: Mode = mode
        self.negative_filter: float = negative_filter
        number_node_map = {
            num: self.__create_node_by_mode(
                SchemaFieldNode(num),
                float(self.min_value),
                float(self.max_value),
                self.mode,
                self.negative_filter,
            )
            for num in self._field_set
        }
        self.number = SpaceFieldSet(self, set(number_node_map.keys()))
        self.__schema_node_map: dict[SchemaObject, Node] = {
            schema_field.schema_obj: node
            for schema_field, node in number_node_map.items()
        }
        self.default_constant_node_input: int | float | None
        match self.mode:
            case Mode.MAXIMUM:
                self.default_constant_node_input = self.max_value
            case Mode.MINIMUM:
                self.default_constant_node_input = self.min_value
            case Mode.SIMILAR:
                self.default_constant_node_input = None
            case _:
                raise ValueError(f"Unknown mode: {self.mode}")

    def _get_node(self, schema: SchemaObject) -> Node[Vector]:
        if node := self.__schema_node_map.get(schema):
            return node
        return self.__create_default_node(schema)

    def _get_all_leaf_nodes(self) -> set[Node[Vector]]:
        return set(self.__schema_node_map.values())

    def __create_node_by_mode(
        self,
        schema_field_node: SchemaFieldNode,
        min_value: float,
        max_value: float,
        mode: Mode,
        negative_filter: float,
    ) -> Node:
        return (
            NumberSimilarityNode(
                schema_field_node, min_value, max_value, negative_filter
            )
            if mode == Mode.SIMILAR
            else NumberEmbeddingNode(
                schema_field_node, min_value, max_value, mode, negative_filter
            )
        )

    def __validate_parameters(
        self, min_value: float | int, max_value: float | int, negative_filter: float
    ) -> None:
        if min_value >= max_value:
            raise InvalidSpaceParamException(
                f"The maximum value ({max_value}) should be greater than the minimum value ({min_value})."
            )
        if negative_filter > 0:
            raise InvalidSpaceParamException(
                f"The negative filter value should not be more than 0. Value is: {negative_filter}"
            )

    def __create_default_node(self, schema: SchemaObject) -> NumberEmbeddingNode:
        if self.mode is Mode.SIMILAR:
            raise NoDefaultNodeException(
                "Number Space with SIMILAR Mode do not have a default value, a .similar "
                "clause is needed in the query."
            )
        constant_node = cast(
            Node, ConstantNode(value=self.default_constant_node_input, schema=schema)
        )

        number_embedding_node = NumberEmbeddingNode(
            parent=constant_node,
            min_value=self.min_value,
            max_value=self.max_value,
            mode=self.mode,
            negative_filter=self.negative_filter,
        )
        self.__schema_node_map[schema] = number_embedding_node
        return number_embedding_node
