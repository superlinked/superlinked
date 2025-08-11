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
from typing_extensions import override

from superlinked.framework.common.dag.custom_node import CustomVectorEmbeddingNode
from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import FloatList
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    VectorAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.custom_embedding_config import (
    CustomEmbeddingConfig,
)
from superlinked.framework.common.space.config.normalization.normalization_config import (
    L2NormConfig,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.dsl.space.has_space_field_set import HasSpaceFieldSet
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet


class CustomSpace(Space[Vector, Vector], HasSpaceFieldSet):
    """
    CustomSpace is the instrument of ingesting your own vectors into Superlinked.
    This way you can use your own vectors right away. What you need to know: (you can use numbering too)
    - vectors need to have the same length
    - vectors will be L2Norm normalized to ensure weighting makes sense
    - weighting can be performed (query-time)
    - you are going to need an FloatList typed SchemaField to supply your data
    - the FloatList field will be able to parse any Sequence[float | int]
    """

    def __init__(
        self,
        vector: FloatList | None | Sequence[FloatList | None],
        length: int,
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
        """
        non_none_vector = self._fields_to_non_none_sequence(vector)
        super().__init__(non_none_vector, FloatList)
        self.vector = SpaceFieldSet[list[float]](self, set(non_none_vector), allowed_param_types=[list[float]])
        self._transformation_config = self._init_transformation_config(length)
        self._schema_node_map = self._calculate_schema_node_map(self._transformation_config)
        self._description = description
        self._length = length

    @property
    @override
    def space_field_set(self) -> SpaceFieldSet:
        return self.vector

    @property
    @override
    def transformation_config(self) -> TransformationConfig[Vector, Vector]:
        return self._transformation_config

    @property
    @override
    def _embedding_node_by_schema(
        self,
    ) -> dict[IdSchemaObject, EmbeddingNode[Vector, Vector]]:
        return self._schema_node_map

    @property
    @override
    def _annotation(self) -> str:
        return f"""{self._description + " " if self._description else ""}Larger positive weights increase the effect on
        similarity compared to other spaces. Affected fields: {self.space_field_set.field_names_text}.
        The space uses already encoded {self._length}
        long vectors. Accepts list[float] type input for a corresponding .similar clause input."""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return False

    def _init_transformation_config(self, length: int) -> TransformationConfig[Vector, Vector]:
        embedding_config = CustomEmbeddingConfig(Vector, length)
        aggregation_config = VectorAggregationConfig(Vector)
        normalization_config = L2NormConfig()
        return TransformationConfig(normalization_config, aggregation_config, embedding_config)

    @override
    def _create_default_node(self, schema: IdSchemaObject) -> EmbeddingNode[Vector, Vector]:
        return CustomVectorEmbeddingNode(None, self.transformation_config, self.vector.fields, schema)

    def _calculate_schema_node_map(
        self, transformation_config: TransformationConfig
    ) -> dict[IdSchemaObject, EmbeddingNode[Vector, Vector]]:
        unchecked_custom_node_map = {
            vector_schema_field: CustomVectorEmbeddingNode(
                parent=SchemaFieldNode(vector_schema_field),
                transformation_config=transformation_config,
                fields_for_identification=self.vector.fields,
            )
            for vector_schema_field in self.vector.fields
        }
        schema_node_map: dict[IdSchemaObject, EmbeddingNode[Vector, Vector]] = {
            schema_field.schema_obj: node for schema_field, node in unchecked_custom_node_map.items()
        }
        return schema_node_map
