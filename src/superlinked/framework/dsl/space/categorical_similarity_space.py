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

from superlinked.framework.common.dag.categorical_similarity_node import (
    CategoricalSimilarityNode,
)
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidSchemaException
from superlinked.framework.common.schema.schema_object import (
    SchemaField,
    SchemaObject,
    String,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet


class CategoricalSimilaritySpace(Space):
    """
    Represents a space for encoding categorical similarity.

    A CategoricalSimilaritySpace is designed to measure the similarity between items that
    are grouped into a finite number of textual categories. The categories are represented
    in a one-hot encoded vector, with the option to apply a negative filter for unmatched
    categories. Negative_filter allows for filtering out unmatched categories, by setting
    it to a large negative value, effectively resulting in large negative similarity between
    non-matching category items. A category input not present in categories will be encoded
    as other category. These categories will be similar to each other by default. Set
    uncategorised_as_category parameter to False in order to suppress this behaviour.

    Attributes:
        category_input (Union[String, List[String]]): The schema field containing input
            category or categories to be considered in the similarity space.
        categories (List[str]): A list of categories that defines the dimensionality of the
            one-hot encoded vector. Any category not listed is considered as 'other'.
        negative_filter (float): A value to represent unmatched categories in the one-hot vector.
            Instead of using 0, which typically represents the absence of a category, this allows
            for a different representation - resulting in effectively filtering out items that has
            non-matching categories.
        uncategorised_as_category (bool): If set to False, the similarity between other categories will be
            set to 0, or negative_filter if set. By this we can control if a category_input not in
            categories will be similar to other category_inputs not in categories. Note that the same
            category_inputs not in categories will not be similar to each other either.

    Raises:
        InvalidSchemaException: If a schema object does not have a corresponding node in the
            similarity space.
    """

    def __init__(
        self,
        category_input: String | list[String],
        categories: list[str],
        negative_filter: float = 0.0,
        uncategorised_as_category: bool = True,
    ) -> None:
        """
        Initialize the CategoricalSimilaritySpace.

        Args:
            category_input (String | list[String]): The category input Schema field.
            categories (list[str]): This controls the set of categories represented in the one-hot vector,
                else it falls into the other category. It is needed to control dimensionality.
            negative_filter (float): Not matched category vector elements are not initialized as 0,
                but as negative_filter
        """
        super().__init__(category_input, String)
        self.__category = SpaceFieldSet(self, cast(set[SchemaField], self._field_set))
        self.__uncategorised_as_category: bool = uncategorised_as_category
        unchecked_category_node_map = {
            single_category: CategoricalSimilarityNode(
                parent=SchemaFieldNode(single_category),
                categories=categories,
                negative_filter=negative_filter,
                uncategorised_as_category=self.uncategorised_as_category,
            )
            for single_category in self._field_set
        }
        self.__schema_node_map: dict[SchemaObject, CategoricalSimilarityNode] = {
            schema_field.schema_obj: node
            for schema_field, node in unchecked_category_node_map.items()
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

    @property
    def uncategorised_as_category(self) -> bool:
        return self.__uncategorised_as_category

    @property
    def category(self) -> SpaceFieldSet:
        return self.__category
