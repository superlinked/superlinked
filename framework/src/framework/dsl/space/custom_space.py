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

from enum import Enum

from beartype.typing import Mapping
from typing_extensions import override

from superlinked.framework.common.dag.custom_node import CustomVectorEmbeddingNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.schema_object import FloatList, SchemaObject
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    VectorAggregation,
    VectorAvg,
)
from superlinked.framework.common.space.normalization import L2Norm, NoNorm
from superlinked.framework.dsl.space.exception import (
    InvalidAggregationStrategyException,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet


class CustomSpace(Space):
    """
    CustomSpace is the instrument of ingesting your own vectors into Superlinked.
    This way you can use your own vectors right away. What you need to know: (you can use numbering too)
    - vectors need to have the same length
    - vectors will be L2Norm normalized to ensure weighting makes sense
    - weighting can be performed (query-time)
    - you are going to need an FloatList typed SchemaField to supply your data
    - the FloatList field will be able to parse any Sequence[float | int]
    - you can leave the aggregation parameter as default, or switch it to using vector averaging during aggregation.
    """

    class AggregationStrategy(Enum):
        """
        Controls how the supplied vectors are aggregated and normalized under the hood. Choose the option most suitable
        for your custom vectors:
            - sum_and_normalize: during aggregation, vectors are summed up elementwise, and normalized using L2 norm
              of the vector to achieve unit vector length when needed.
            - vector_average: vectors are summed up elementwise in case of aggregation, and normalized using the
              number of the aggregated vectors to achieve < 1 length.
              This policy expects vectors that are roughly unit length. Use it for vectors that are incompatible with L2
              normalization.
        """

        SUM_AND_NORMALIZE = "sum_and_normalize"
        VECTOR_AVERAGE = "vector_average"

    def __init__(
        self,
        vector: FloatList | list[FloatList],
        length: int,
        aggregation: AggregationStrategy = AggregationStrategy.SUM_AND_NORMALIZE,
        description: str | None = None,
    ) -> None:
        """
        Initializes a CustomSpace for vector storage and manipulation within Superlinked.

        This constructor sets up a space designed for custom vector ingestion, allowing users to specify how these
        vectors are aggregated and normalized.

        Args:
            vector (FloatList | list[FloatList]): The input vector(s) to be stored in the space.
              This can be a single FloatList SchemaField or a list of those.
            length (int): The fixed length that all vectors in this space must have. This ensures uniformity and
              consistency in vector operations.
            aggregation (AggregationStrategy, optional): The strategy to use for aggregating multiple vectors.
              This can be either `SUM_AND_NORMALIZE` for summing vectors and normalizing to unit length,
              or `VECTOR_AVERAGE` for averaging vectors during aggregation, but not performing other normalization.
              Defaults to `SUM_AND_NORMALIZE`.

        Raises:
            InvalidAggregationStrategyException: If the specified aggregation strategy is not recognized. This ensures
              that only valid aggregation strategies are used.
        """
        super().__init__(vector, FloatList)
        self._description = description
        aggregation_strategy: Aggregation
        match aggregation:
            case self.AggregationStrategy.SUM_AND_NORMALIZE:
                aggregation_strategy = VectorAggregation(L2Norm())
            case self.AggregationStrategy.VECTOR_AVERAGE:
                aggregation_strategy = VectorAvg(NoNorm())
            case _:
                raise InvalidAggregationStrategyException(
                    f"Invalid aggregation strategy. Should be one of AggregationStrategy Enum. Got {aggregation=}."
                )
        unchecked_custom_node_map = {
            vector: CustomVectorEmbeddingNode(
                parent=SchemaFieldNode(vector),
                length=length,
                aggregation=aggregation_strategy,
            )
            for vector in self._field_set
        }
        self.vector = SpaceFieldSet(self, self._field_set)
        self.__schema_node_map: dict[SchemaObject, CustomVectorEmbeddingNode] = {
            schema_field.schema_obj: node
            for schema_field, node in unchecked_custom_node_map.items()
        }
        self._length = length

    @property
    def _node_by_schema(self) -> Mapping[SchemaObject, Node[Vector]]:
        return self.__schema_node_map

    @property
    @override
    def annotation(self) -> str:
        return f"""{self._description + " " if self._description else ""}Larger positive weights increase the effect on
        similarity compared to other spaces.
        Space weights do not matter if there is only 1 space in the query. The space uses already encoded {self._length}
        long vectors. Accepts list[float] type input for a corresponding .similar clause input."""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return False
