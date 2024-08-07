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

import math

from beartype.typing import Mapping, cast
from typing_extensions import override

from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.number_embedding_node import (
    NumberEmbeddingNode,
    NumberEmbeddingParams,
)
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.number_embedding import (
    LinearScale,
    LogarithmicScale,
    Mode,
    Scale,
)
from superlinked.framework.common.schema.schema_object import Number, SchemaObject
from superlinked.framework.common.space.aggregation import InputAggregationMode
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
            It must larger or equal to 0 in case of scale=LogarithmicScale(base).
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
            It cannot be 0 in case of scale=LogarithmicScale(base).
        mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
            Similar mode expects a .similar on the query, otherwise it will default to maximum.
        scale (Scale): The scaling of the number embedding.
            Possible values are: LinearScale(), and LogarithmicScale(base).
            LogarithmicScale base must be larger than 1. It defaults to LinearScale().
        aggregation_mode (InputAggregationMode): The  aggregation mode of the number embedding.
            Possible values are: maximum, minimum and average.
        negative_filter (float): This is a value that will be set for everything that is equal or
            lower than the min_value. It can be a float. It defaults to 0 (No effect)

    Raises:
        InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
            Or the min_value is bigger than the max value, or the negative filter bigger than 0
        InvalidSchemaException: If there's no node corresponding to a given schema.

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        number: Number | list[Number],
        min_value: float | int,
        max_value: float | int,
        mode: Mode,
        scale: Scale = LinearScale(),
        aggregation_mode: InputAggregationMode = InputAggregationMode.INPUT_AVERAGE,
        negative_filter: float = 0.0,
    ) -> None:
        """
        Initializes the NumberSpace object.

        Attributes:
            number (SpaceFieldSet): A set of Number objects.
                It is a SchemaFieldObject not regular python ints or floats.
            min_value (float | int): This represents the minimum boundary. Any number lower than
                this will be considered as this minimum value. It can be either a float or an integer.
                It must larger or equal to 0 in case of scale=LogarithmicScale(base).
            max_value (float | int): This represents the maximum boundary. Any number higher than
                this will be considered as this maximum value. It can be either a float or an integer.
                It cannot be 0 in case of scale=LogarithmicScale(base).
            mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
                Similar mode expects a .similar on the query, otherwise it will default to maximum.
            scale (Scale): The scaling of the number embedding.
                Possible values are: LinearScale(), and LogarithmicScale(base).
                LogarithmicScale base must be larger than 1. It defaults to LinearScale().
            aggregation_mode (InputAggregationMode): The  aggregation mode of the number embedding.
                Possible values are: maximum, minimum and average.
            negative_filter (float): This is a value that will be set for everything that is equal or
                lower than the min_value. It can be a float. It defaults to 0 (No effect)

         Raises:
            InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
                Or the min_value is bigger than the max value, or the negative filter bigger than 0
            InvalidSchemaException: If there's no node corresponding to a given schema.
        """
        self.aggregation_mode = aggregation_mode
        super().__init__(number, Number)
        self.__validate_parameters(min_value, max_value, negative_filter)
        self.embedding_params = NumberEmbeddingParams(
            min_value=float(min_value),
            max_value=float(max_value),
            mode=mode,
            scale=scale,
            negative_filter=negative_filter,
        )
        self.default_constant_node_input: int | float | None
        match mode:
            case Mode.MAXIMUM:
                self.default_constant_node_input = max_value
            case Mode.MINIMUM:
                self.default_constant_node_input = min_value
            case Mode.SIMILAR:
                self.default_constant_node_input = None
            case _:
                raise ValueError(f"Unknown mode: {mode}")
        number_node_map = {
            num: NumberEmbeddingNode(
                SchemaFieldNode(num), self.embedding_params, self.aggregation_mode
            )
            for num in self._field_set
        }
        self.number = SpaceFieldSet(self, set(number_node_map.keys()))
        self.__schema_node_map: dict[SchemaObject, Node] = {
            schema_field.schema_obj: node
            for schema_field, node in number_node_map.items()
        }

    @property
    def _node_by_schema(self) -> Mapping[SchemaObject, Node[Vector]]:
        return self.__schema_node_map

    @property
    @override
    def annotation(self) -> str:
        mode_text = self.embedding_params.mode.value
        mode_to_preference: dict[str, str] = {
            "minimum": "lower",
            "maximum": "higher",
            "similar": "similar",
        }
        similar_first_text = (
            """
            s to the one supplied in a .similar clause during a Query.
            """
            if self.embedding_params.mode == Mode.SIMILAR
            else ""
        )
        negative_text: dict[str, str] = {
            "similar": "the values further from the value in the corresponding mandatory similar clause.",
            "minimum": "higher values",
            "maximum": "lower values",
        }
        end_text: str = (
            " Accepts int or float type input for a corresponding .similar clause input."
            if self.embedding_params.mode == Mode.SIMILAR
            else ""
        )
        scaling_text = (
            f"logarithmically with the base of {self.embedding_params.scale.base}"
            if isinstance(self.embedding_params.scale, LogarithmicScale)
            else "linearly"
        )
        min_value = (
            math.log(
                1 + self.embedding_params.min_value,
                self.embedding_params.scale.base,
            )
            if isinstance(self.embedding_params.scale, LogarithmicScale)
            else self.embedding_params.min_value
        )
        max_value = (
            math.log(
                1 + self.embedding_params.max_value,
                self.embedding_params.scale.base,
            )
            if isinstance(self.embedding_params.scale, LogarithmicScale)
            else self.embedding_params.max_value
        )
        return f"""The space encodes numbers between {min_value}
        and {max_value}, being the domain of the space.
        Values are {scaling_text} spaced in {min_value} and {max_value}.
        It has {mode_text} Mode so it favors the {mode_to_preference[mode_text]} number{similar_first_text}.
        For this {mode_text} mode space, negative weights mean favoring
        the {negative_text[mode_text]}. 0 weight means insensitivity.
        Larger positive weights increase the effect on similarity compared to other spaces. Space weights do not matter
        if there is only 1 space in the query.{end_text}"""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return self.aggregation_mode == Mode.SIMILAR

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

    @override
    def _handle_node_not_present(self, schema: SchemaObject) -> NumberEmbeddingNode:
        if self.embedding_params.mode is Mode.SIMILAR:
            raise NoDefaultNodeException(
                "Number Space with SIMILAR Mode do not have a default value, a .similar "
                "clause is needed in the query."
            )
        constant_node = cast(
            Node, ConstantNode(value=self.default_constant_node_input, schema=schema)
        )

        number_embedding_node = NumberEmbeddingNode(
            constant_node, self.embedding_params, self.aggregation_mode
        )
        self.__schema_node_map[schema] = number_embedding_node
        return number_embedding_node
