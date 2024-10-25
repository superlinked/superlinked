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

from superlinked.framework.common.dag.chunking_node import ChunkingNode
from superlinked.framework.common.dag.comparison_filter_node import ComparisonFilterNode
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.dag.exception import LeafNodeCountException
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.compiler.query.query_node_registry import QueryNodeRegistry
from superlinked.framework.query.dag.query_dag import QueryDag
from superlinked.framework.query.dag.query_node import QueryNode

NODES_TO_EXCLUDE = (
    ChunkingNode,
    ComparisonFilterNode,
    EventAggregationNode,
    SchemaFieldNode,
)


class QueryDagCompiler:
    def __init__(self, store_compilation_results: bool = True) -> None:
        self.__store_compilation_results = store_compilation_results
        self.__compiled_node_by_node_id: dict[str, QueryNode] = {}
        self.__query_node_registry = QueryNodeRegistry()

    def compile_node(
        self,
        node: Node,
    ) -> QueryNode | None:
        if isinstance(node, NODES_TO_EXCLUDE):
            return None
        if compiled_node := self.__compiled_node_by_node_id.get(node.node_id):
            return compiled_node
        compiled_parents = [self.compile_node(parent) for parent in node.parents]
        compiled_node = self.__query_node_registry.init_compiled_node(
            node,
            [
                compiled_parent
                for compiled_parent in compiled_parents
                if compiled_parent is not None
            ],
        )
        self.__compiled_node_by_node_id[node.node_id] = compiled_node
        return compiled_node

    def compile_dag(self, dag: Dag) -> QueryDag:
        compiled_index_node = self.compile_node(dag.index_node)
        if compiled_index_node is None:
            raise LeafNodeCountException("Cannot compile index node.")
        query_dag = QueryDag(list(self.__compiled_node_by_node_id.values()))
        if not self.__store_compilation_results:
            self.__compiled_node_by_node_id = {}
        return query_dag
