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
from typing_extensions import override

from superlinked.framework.common.dag.categorical_similarity_node import (
    CategoricalSimilarityNode,
)
from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.schema_object import (
    SchemaField,
    SchemaObject,
    String,
    StringList,
)
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    VectorAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.categorical_similarity_embedding_config import (
    CategoricalSimilarityEmbeddingConfig,
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


class CategoricalSimilaritySpace(Space[Vector, list[str]], HasSpaceFieldSet):
    """
    Represents a space for encoding categorical similarity.

    A CategoricalSimilaritySpace is designed to measure the similarity between items that
    are grouped into a finite number of textual categories. The categories are represented
    in an n-hot encoded vector, with the option to apply a negative filter for unmatched
    categories, enhancing the distinction between matching and non-matching category items.
    Negative_filter allows for filtering out unmatched categories, by setting
    it to a large negative value, effectively resulting in large negative similarity between
    non-matching category items. A category input not present in categories will be encoded
    as `other` category. These categories will be similar to each other by default. Set
    uncategorized_as_category parameter to False in order to suppress this behavior - this
    way other categories are not similar to each other in any case - not even to the same
    `other` category. To make that specific category value similar to only the same category
    items, consider adding it to `categories`.

    Attributes:
        category_input (StringList | String | list[String | StringList]):
            The schema field containing input categories to be considered in the similarity space.
            Input contains one or more categories in a list if `StringList` is provided.
            If `String` is provided, then the input must be a single value.
        categories (List[str]): A list of categories that defines the dimensionality of the
            one-hot encoded vector. Any category not listed is considered as 'other'.
        negative_filter (float): A value to represent unmatched categories in the one-hot vector.
            Instead of using 0, which typically represents the absence of a category, this allows
            for a different representation - resulting in effectively filtering out items that has
            non-matching categories.
        uncategorized_as_category (bool): If set to False, the similarity between other categories will be
            set to 0, or negative_filter if set. By this we can control if a category_input not in
            categories will be similar to other category_inputs not in categories. Note that the same
            category_inputs not in categories will not be similar to each other either.
    Raises:
        InvalidSchemaException: If a schema object does not have a corresponding node in the
            similarity space.
    """

    def __init__(
        self,
        category_input: StringList | String | list[String | StringList],
        categories: list[str],
        negative_filter: float = 0.0,
        uncategorized_as_category: bool = True,
    ) -> None:
        """
        Initializes a new instance of the CategoricalSimilaritySpace.

        This constructor sets up the space with the necessary configurations to encode and measure categorical
        similarity based on the provided parameters.

        Args:
            category_input (StringList | String | list[String | StringList]):
            The schema field containing input categories to be considered in the similarity space.
            Input contains one or more categories in a list if `StringList` is provided.
            If `String` is provided, then the input must be a single value.
            categories (list[str]): A list of all the recognized categories. Categories not included in this list will
                be treated as 'other', unless `uncategorized_as_category` is False.
            negative_filter (float, optional): A value used to represent unmatched categories in the encoding process.
                This allows for a penalizing non-matching categories - in contrast to them contributing 0 to similarity,
                 it is possible to influence the similarity score negatively. Defaults to 0.0.
            uncategorized_as_category (bool, optional): Determines whether categories not listed in `categories` should
                be treated as a distinct 'other' category. Defaults to True.

        Raises:
            InvalidSchemaException: If a schema object does not have a corresponding node in the similarity space,
            indicating a configuration or implementation error.
        """
        # TODO this type ignore is not needed but linting is flaky in CI
        super().__init__(
            category_input,
            String | StringList,  # type: ignore[misc] # interface supports only one type
        )
        self._embedding_config = CategoricalSimilarityEmbeddingConfig(
            list[str],
            categories=categories,
            uncategorized_as_category=uncategorized_as_category,
            negative_filter=negative_filter,
        )
        self._transformation_config = self._init_transformation_config(
            self._embedding_config
        )
        self.__category = SpaceFieldSet[list[str]](
            self,
            set(
                category_input if isinstance(category_input, list) else [category_input]
            ),
        )
        unchecked_category_node_map = {
            single_category: CategoricalSimilarityNode(
                parent=SchemaFieldNode(cast(SchemaField, single_category)),
                transformation_config=self.transformation_config,
            )
            for single_category in (
                category_input if isinstance(category_input, list) else [category_input]
            )
        }
        self.__schema_node_map: dict[SchemaObject, EmbeddingNode[Vector, list[str]]] = {
            schema_field.schema_obj: node
            for schema_field, node in unchecked_category_node_map.items()
        }

    @property
    @override
    def _node_by_schema(
        self,
    ) -> dict[SchemaObject, EmbeddingNode[Vector, list[str]]]:
        return self.__schema_node_map

    def _init_transformation_config(
        self, embedding_config: CategoricalSimilarityEmbeddingConfig
    ) -> TransformationConfig[Vector, list[str]]:
        aggregation_config = VectorAggregationConfig(Vector)
        normalization_config = L2NormConfig()
        return TransformationConfig(
            normalization_config, aggregation_config, embedding_config
        )

    @override
    def _create_default_node(
        self, schema: SchemaObject
    ) -> EmbeddingNode[Vector, list[str]]:
        zero_vector = Vector.init_zero_vector(self.length)
        constant_node = cast(Node, ConstantNode(value=zero_vector, schema=schema))
        default_node = CategoricalSimilarityNode(
            constant_node, self.transformation_config
        )
        return default_node

    @property
    @override
    def space_field_set(self) -> SpaceFieldSet:
        return self.category

    @property
    @override
    def transformation_config(self) -> TransformationConfig[Vector, list[str]]:
        return self._transformation_config

    @property
    @override
    def annotation(self) -> str:
        not_text_for_uncategorized = (
            "" if self._embedding_config.uncategorized_as_category else " not"
        )
        return f"""The space creates a one-hot encoding where its value can be one or more
        of {str(self._embedding_config.categories)}.
        Other values do{not_text_for_uncategorized} have a separate other category,
        so these are{not_text_for_uncategorized} similar to each other.
        Not matching categories are creating {self._embedding_config.negative_filter}
        similarity contribution.
        There has to be a .similar clause in the Query corresponding to this space.
        Negative weights mean similarity to anything but that category,
        positive weights mean similar to the categories in the .similar clause, 0 weight means insensitivity.
        Larger positive weights increase the effect on similarity compared to other spaces. Space weights do not
        matter if there is only 1 space in the query.
        Accepts str or list[str] type input for a corresponding .similar clause input."""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return False

    @property
    def uncategorized_as_category(self) -> bool:
        return self._embedding_config.uncategorized_as_category

    @property
    def category(self) -> SpaceFieldSet:
        return self.__category
