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

from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.query.dag.query_embedding_orphan_node import (
    QueryEmbeddingOrphanNode,
)
from superlinked.framework.query.dag.query_node import QueryNode


class QueryImageEmbeddingNode(QueryEmbeddingOrphanNode[Vector, ImageEmbeddingNode, ImageData]):
    def __init__(self, node: ImageEmbeddingNode, parents: Sequence[QueryNode]) -> None:
        super().__init__(node, parents, ImageData)
