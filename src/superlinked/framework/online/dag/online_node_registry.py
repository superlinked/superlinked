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

import inspect
from pydoc import locate

from beartype.typing import TypeVar, cast

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.exception import NotImplementedException
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.online_aggregation_node import (
    OnlineAggregationNode,
)
from superlinked.framework.online.dag.online_categorical_similarity_node import (
    OnlineCategoricalSimilarityNode,
)
from superlinked.framework.online.dag.online_chunking_node import OnlineChunkingNode
from superlinked.framework.online.dag.online_comparison_filter_node import (
    OnlineComparisonFilterNode,
)
from superlinked.framework.online.dag.online_concatenation_node import (
    OnlineConcatenationNode,
)
from superlinked.framework.online.dag.online_constant_node import OnlineConstantNode
from superlinked.framework.online.dag.online_custom_node import (
    OnlineCustomVectorEmbeddingNode,
)
from superlinked.framework.online.dag.online_event_aggregation_node import (
    OnlineEventAggregationNode,
)
from superlinked.framework.online.dag.online_index_node import OnlineIndexNode
from superlinked.framework.online.dag.online_named_function_node import (
    OnlineNamedFunctionNode,
)
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.online_number_embedding_node import (
    OnlineNumberEmbeddingNode,
)
from superlinked.framework.online.dag.online_recency_node import OnlineRecencyNode
from superlinked.framework.online.dag.online_schema_field_node import (
    OnlineSchemaFieldNode,
)
from superlinked.framework.online.dag.online_text_embedding_node import (
    OnlineTextEmbeddingNode,
)

LNT = TypeVar("LNT", type[Node], type[OnlineNode])
DEFAULT_NODE_TYPES: list[type[OnlineNode]] = [
    OnlineAggregationNode,
    OnlineChunkingNode,
    OnlineCategoricalSimilarityNode,
    OnlineComparisonFilterNode,
    OnlineConcatenationNode,
    OnlineConstantNode,
    OnlineCustomVectorEmbeddingNode,
    OnlineEventAggregationNode,
    OnlineIndexNode,
    OnlineNamedFunctionNode,
    OnlineNumberEmbeddingNode,
    OnlineRecencyNode,
    OnlineSchemaFieldNode,
    OnlineTextEmbeddingNode,
    # * Add new OnlineNode implementations here
]


class OnlineNodeRegistry:
    _instance = None

    def __new__(cls) -> "OnlineNodeRegistry":
        if cls._instance is None:
            cls._instance = super(OnlineNodeRegistry, cls).__new__(cls)
            cls.online_node_type_by_node_type: dict[type[Node], type[OnlineNode]] = {
                cls.get_node_type(node): node for node in DEFAULT_NODE_TYPES
            }
        return cls._instance

    @classmethod
    def get_node_type(cls, node: type[OnlineNode]) -> type[Node]:
        """
        Checks if OnlineNode child implements OnlineNode containing Node child Generic type.
        If yes, returns that Node child type.
        """
        node_bases = getattr(node, "__orig_bases__", [])
        for base in node_bases:
            if issubclass(base.__origin__, OnlineNode):
                for arg in getattr(base, "__args__", []):
                    if inspect.isclass(arg) and issubclass(arg, Node):
                        return arg
                    origin = getattr(arg, "__origin__", None)
                    if origin and issubclass(origin, Node):
                        return origin
        raise NotImplementedException("Node type not found for OnlineNode.")

    def register_node(self, node: type[Node], online_node: type[OnlineNode]) -> None:
        self.online_node_type_by_node_type[node] = online_node

    def register_node_by_path(self, node_path: str, online_node_path: str) -> None:
        node_class = self.__import_node_class(node_path, Node)  # type: ignore[type-abstract]
        online_node_class = self.__import_node_class(
            online_node_path,
            OnlineNode,  # type: ignore[type-abstract]
        )
        self.online_node_type_by_node_type[node_class] = online_node_class

    def __import_node_class(self, path: str, expected_class: LNT) -> LNT:
        node_class = locate(path)
        if not isinstance(node_class, type):
            raise ValueError(f"Not a valid class path: {path}")
        if not issubclass(node_class, expected_class):
            raise ValueError(
                f"Not {expected_class.__name__} type: {node_class.__name__}"
            )
        return cast(LNT, node_class)

    def init_online_node(
        self,
        node: Node,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> OnlineNode:
        online_node_class = self.online_node_type_by_node_type.get(type(node))
        if not online_node_class:
            raise NotImplementedException(
                f"Not implemented Node type: {node.__class__.__name__}"
            )
        return online_node_class(node, parents, storage_manager)
