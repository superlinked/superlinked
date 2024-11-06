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

from superlinked.framework.compiler.compiled_node_registry import CompiledNodeRegistry
from superlinked.framework.query.dag.query_aggregation_node import QueryAggregationNode
from superlinked.framework.query.dag.query_categorical_similarity_node import (
    QueryCategoricalSimilarityNode,
)
from superlinked.framework.query.dag.query_concatenation_node import (
    QueryConcatenationNode,
)
from superlinked.framework.query.dag.query_constant_node import QueryConstantNode
from superlinked.framework.query.dag.query_custom_vector_embedding_node import (
    QueryCustomVectorEmbeddingNode,
)
from superlinked.framework.query.dag.query_image_embedding_node import (
    QueryImageEmbeddingNode,
)
from superlinked.framework.query.dag.query_index_node import QueryIndexNode
from superlinked.framework.query.dag.query_named_function_node import (
    QueryNamedFunctionNode,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.dag.query_number_embedding_node import (
    QueryNumberEmbeddingNode,
)
from superlinked.framework.query.dag.query_recency_node import QueryRecencyNode
from superlinked.framework.query.dag.query_text_embedding_node import (
    QueryTextEmbeddingNode,
)

DEFAULT_NODE_TYPES: list[type[QueryNode]] = [
    QueryAggregationNode,
    QueryCategoricalSimilarityNode,
    QueryConcatenationNode,
    QueryConstantNode,
    QueryCustomVectorEmbeddingNode,
    QueryImageEmbeddingNode,
    QueryIndexNode,
    QueryNamedFunctionNode,
    QueryNumberEmbeddingNode,
    QueryRecencyNode,
    QueryTextEmbeddingNode,
    # * Add new QueryNode implementations here
]


class QueryNodeRegistry(CompiledNodeRegistry[QueryNode]):
    def __init__(self) -> None:
        # This type ignore is a python "bug", we cannot pass an abstract class
        # when it's type-hinted as type.
        super().__init__(QueryNode, DEFAULT_NODE_TYPES)  # type: ignore
