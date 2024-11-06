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

from typing_extensions import override

from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.number_embedding_node import NumberEmbeddingNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.schema.schema_object import Number, SchemaObject
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationConfig,
    AvgAggregationConfig,
    MaxAggregationConfig,
    MinAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.number_embedding_config import (
    LinearScale,
    LogarithmicScale,
    Mode,
    NumberEmbeddingConfig,
    Scale,
)
from superlinked.framework.common.space.config.normalization.normalization_config import (
    NoNormConfig,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.util.lazy_property import lazy_property
from superlinked.framework.dsl.space.exception import NoDefaultNodeException
from superlinked.framework.dsl.space.has_space_field_set import HasSpaceFieldSet
from superlinked.framework.dsl.space.input_aggregation_mode import InputAggregationMode
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet


class NumberSpace(Space[float, float], HasSpaceFieldSet):
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
        """
        self._aggregation_mode = aggregation_mode  # this must be set before super init for _handle_node_not_present
        super().__init__(number, Number)
        self._aggregation_config_type_by_mode = (
            self.__init_aggregation_config_type_by_mode()
        )
        self._embedding_config = NumberEmbeddingConfig(
            float,
            float(min_value),
            float(max_value),
            mode,
            scale,
            negative_filter,
        )
        self._transformation_config = self._init_transformation_config(
            self._embedding_config, self._aggregation_mode
        )
        number_node_map = {
            num: NumberEmbeddingNode(
                parent=SchemaFieldNode(num),
                transformation_config=self._transformation_config,
            )
            for num in (number if isinstance(number, list) else [number])
        }
        self.number = SpaceFieldSet[float](self, set(number_node_map.keys()))
        self.__schema_node_map: dict[SchemaObject, EmbeddingNode[float, float]] = {
            schema_field.schema_obj: node
            for schema_field, node in number_node_map.items()
        }

    @property
    @override
    def _node_by_schema(
        self,
    ) -> dict[SchemaObject, EmbeddingNode[float, float]]:
        return self.__schema_node_map

    @property
    @override
    def space_field_set(self) -> SpaceFieldSet:
        return self.number

    @property
    @override
    def transformation_config(self) -> TransformationConfig[float, float]:
        return self._transformation_config

    def __init_aggregation_config_type_by_mode(
        self,
    ) -> dict[InputAggregationMode, type[AggregationConfig]]:
        return {
            InputAggregationMode.INPUT_AVERAGE: AvgAggregationConfig,
            InputAggregationMode.INPUT_MINIMUM: MinAggregationConfig,
            InputAggregationMode.INPUT_MAXIMUM: MaxAggregationConfig,
        }

    @property
    @override
    def annotation(self) -> str:
        mode_text = self._embedding_config.mode.value
        mode_to_preference: dict[str, str] = {
            "minimum": "lower",
            "maximum": "higher",
            "similar": "similar",
        }
        similar_first_text = (
            """
            s to the one supplied in a .similar clause during a Query.
            """
            if self._embedding_config.mode == Mode.SIMILAR
            else ""
        )
        negative_text: dict[str, str] = {
            "similar": "the values further from the value in the corresponding mandatory similar clause.",
            "minimum": "higher values",
            "maximum": "lower values",
        }
        end_text: str = (
            " Accepts int or float type input for a corresponding .similar clause input."
            if self._embedding_config.mode == Mode.SIMILAR
            else ""
        )
        scaling_text = (
            f"logarithmically with the base of {self._embedding_config.scale.base}"
            if isinstance(self._embedding_config.scale, LogarithmicScale)
            else "linearly"
        )
        min_value = (
            math.log(
                1 + self._embedding_config.min_value,
                self._embedding_config.scale.base,
            )
            if isinstance(self._embedding_config.scale, LogarithmicScale)
            else self._embedding_config.min_value
        )
        max_value = (
            math.log(
                1 + self._embedding_config.max_value,
                self._embedding_config.scale.base,
            )
            if isinstance(self._embedding_config.scale, LogarithmicScale)
            else self._embedding_config.max_value
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
        return self._aggregation_mode == Mode.SIMILAR

    def _init_transformation_config(
        self,
        embedding_config: NumberEmbeddingConfig,
        aggregation_mode: InputAggregationMode,
    ) -> TransformationConfig[float, float]:
        aggregation_config = self._aggregation_config_type_by_mode[aggregation_mode](
            float
        )
        normalization_config = NoNormConfig()
        return TransformationConfig(
            normalization_config, aggregation_config, embedding_config
        )

    @override
    def _create_default_node(self, schema: SchemaObject) -> EmbeddingNode[float, float]:
        constant_node = ConstantNode(
            value=self._default_constant_node_input, schema=schema
        )
        default_node = NumberEmbeddingNode(
            parent=constant_node,
            transformation_config=self._transformation_config,
        )
        return default_node

    @lazy_property
    def _default_constant_node_input(self) -> float:
        match self._embedding_config.mode:
            case Mode.MAXIMUM:
                default_constant_node_input = self._embedding_config.max_value
            case Mode.MINIMUM:
                default_constant_node_input = self._embedding_config.min_value
            case Mode.SIMILAR:
                raise NoDefaultNodeException(
                    "Number Space with SIMILAR Mode do not have a default value, a .similar "
                    "clause is needed in the query."
                )
            case _:
                raise ValueError(f"Unknown mode: {self._embedding_config.mode}")
        return default_constant_node_input
