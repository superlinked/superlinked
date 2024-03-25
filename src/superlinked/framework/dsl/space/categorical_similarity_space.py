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
    A text similarity space is used to to reflect similarity between items grouped into a finite number of categories.
    Not necessarily just already grouped items: similarity in terms of scalars can also be expressed this way.
    Scalars need to be first grouped into bins, and from there the process is similar.
    """

    def __init__(
        self,
        category: String | list[String],
        categories: list[str],
        negative_filter: float = 0.0,
    ) -> None:
        """
        Initialize the CategoricalSimilaritySpace.

        Args:
            category (string): The category input
            categories (list[str]): This controls the set of categories represented in the one-hot vector,
                else it falls into the other category. It is needed to control dimensionality.
            negative_filter (float): Not matched category vector elements are not initialized as 0,
                but as negative_filter
        """
        super().__init__(category, String)
        unchecked_category_node_map = {
            single_category: CategoricalSimilarityNode(
                parent=SchemaFieldNode(single_category),
                categories=categories,
                negative_filter=negative_filter,
            )
            for single_category in self._field_set
        }
        self.category = SpaceFieldSet(self, cast(set[SchemaField], self._field_set))
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
