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

from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
from beartype.typing import Sequence

from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.categorical_similarity_node import (
    CategoricalSimilarityNode,
)
from superlinked.framework.common.dag.chunking_node import ChunkingNode
from superlinked.framework.common.dag.comparison_filter_node import ComparisonFilterNode
from superlinked.framework.common.dag.concatenation_node import ConcatenationNode
from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.custom_node import CustomVectorEmbeddingNode
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.dag.named_function_node import NamedFunctionNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.number_embedding_node import NumberEmbeddingNode
from superlinked.framework.common.dag.recency_node import RecencyNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.dag.text_embedding_node import TextEmbeddingNode

HIGHT_BY_NODE_TYPE = {
    IndexNode: 0.0,
    ConcatenationNode: 1.0,
    AggregationNode: 2.0,
    EventAggregationNode: 3.0,
    CategoricalSimilarityNode: 4.0,
    CustomVectorEmbeddingNode: 4.0,
    ImageEmbeddingNode: 4.0,
    NumberEmbeddingNode: 4.0,
    RecencyNode: 4.0,
    TextEmbeddingNode: 4.0,
    ComparisonFilterNode: 4.0,
    ChunkingNode: 5.0,
    ConstantNode: 6.0,
    NamedFunctionNode: 6.0,
    SchemaFieldNode: 6.0,
}

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LETTER_COUNT = len(LETTERS)


class DagDisplayer:
    def __init__(self) -> None:
        self.__graph = nx.DiGraph()
        self.__node_positions = dict[str, list[float]]()
        self.__node_count_by_level: dict[float, float | int] = defaultdict(int)
        self.__node_count_by_level.update(
            {HIGHT_BY_NODE_TYPE[node_type]: 0.3 for node_type in [ChunkingNode, SchemaFieldNode, TextEmbeddingNode]}
        )
        self.__node_label_by_node_str = dict[str, str]()

    def traverse(self, dag: Dag) -> None:
        visited_nodes = list[Node]()
        unvisited_elements: list[Node] = [dag.index_node]
        self.__node_positions[self.__get_node_str(dag.index_node)] = [0.0, 1.0]
        while unvisited_elements:
            node = unvisited_elements.pop()
            level = HIGHT_BY_NODE_TYPE[type(node)]
            visited_nodes.append(node)
            node_label = self.__get_node_label(node)
            self.__add_edge(node_label, level, node.parents)
            unvisited_elements.extend([parent for parent in node.parents if parent not in visited_nodes])

    def show(self) -> None:
        nx.draw_networkx_nodes(
            self.__graph, self.__node_positions, cmap=plt.get_cmap("jet"), node_size=500  # type: ignore # it has
        )
        nx.draw_networkx_labels(self.__graph, self.__node_positions)
        nx.draw_networkx_edges(
            self.__graph, self.__node_positions, edgelist=self.__graph.edges(), edge_color="r", arrows=True
        )
        plt.legend(
            labels=[f"{label} = {node_str}" for node_str, label in self.__node_label_by_node_str.items()],
            handletextpad=-0.5,  # type: ignore # valid param
            handlelength=0,  # type: ignore # valid param
            fontsize=6,  # type: ignore # valid param
        )
        plt.show()

    def __add_edge(self, node_label: str, level: float, parents: Sequence[Node]) -> None:
        self.__node_positions[node_label] = [self.__node_count_by_level[level], level]
        self.__node_count_by_level[level] = self.__node_count_by_level[level] + 1
        self.__graph.add_edges_from([(self.__get_node_label(parent), node_label) for parent in parents])

    def __get_node_label(self, node: Node) -> str:
        node_str = self.__get_node_str(node)
        if label := self.__node_label_by_node_str.get(node_str):
            return label
        node_index = len(self.__node_label_by_node_str)
        node_label = self.__calculate_node_label_letter(node_index)
        self.__node_label_by_node_str[node_str] = node_label
        return node_label

    @staticmethod
    def __get_node_str(node: Node) -> str:
        schemas = ", ".join([s._schema_name for s in node.schemas])
        suffix = (
            f"({node.schema_field.schema_obj._schema_name}.{node.schema_field.name})"
            if isinstance(node, SchemaFieldNode)
            else f"({schemas})"
        )
        return f"{type(node).__name__}{suffix}({len(node.parents)} parents) ({node.node_id})"

    @staticmethod
    def __calculate_node_label_letter(index: int) -> str:
        if index < LETTER_COUNT:
            return LETTERS[index]
        level_index = index % LETTER_COUNT
        return (
            DagDisplayer.__calculate_node_label_letter(((index - level_index) // LETTER_COUNT) - 1)
            + LETTERS[level_index]
        )
