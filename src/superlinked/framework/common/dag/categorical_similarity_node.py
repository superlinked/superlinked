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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.categorical_similarity_embedding import (
    CategoricalSimilarityEmbedding,
    CategoricalSimilarityParams,
)
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import (
    Aggregation,
    VectorAggregation,
)
from superlinked.framework.common.space.normalization import L2Norm


class CategoricalSimilarityNode(Node[Vector], HasLength, HasAggregation):
    def __init__(
        self,
        parent: Node[str],
        categorical_similarity_param: CategoricalSimilarityParams,
    ) -> None:
        super().__init__(Vector, [parent])
        self.__aggregation = VectorAggregation(L2Norm())
        self.embedding = CategoricalSimilarityEmbedding(
            categorical_similarity_param=categorical_similarity_param,
            normalization=self.__aggregation.normalization,
        )

    @property
    def length(self) -> int:
        return self.embedding.length

    @property
    @override
    def aggregation(self) -> Aggregation:
        return self.__aggregation

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "categories": self.embedding.categories,
            "negative_filter": self.embedding.negative_filter,
            "uncategorized_as_category": self.embedding.uncategorized_as_category,
            "aggregation": self.__aggregation,
        }
