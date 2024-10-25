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

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_dag import SchemaDag
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.compiler.online.online_node_registry import (
    OnlineNodeRegistry,
)
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.online_schema_dag import OnlineSchemaDag


class OnlineSchemaDagCompiler:
    def __init__(
        self, nodes: set[Node], store_compilation_results: bool = True
    ) -> None:
        self.__nodes = nodes
        self.__store_compilation_results = store_compilation_results
        self.__compiled_node_by_node_id: dict[str, OnlineNode] = {}
        self.__online_node_registry = OnlineNodeRegistry()

    def compile_node(
        self,
        node: Node,
        storage_manager: StorageManager,
    ) -> OnlineNode:
        if compiled_node := self.__compiled_node_by_node_id.get(node.node_id):
            return compiled_node
        compiled_parents = [
            self.compile_node(parent, storage_manager)
            for parent in node.parents
            if parent in self.__nodes
        ]
        compiled_node = self.__online_node_registry.init_compiled_node(
            node, compiled_parents, storage_manager
        )
        self.__compiled_node_by_node_id[node.node_id] = compiled_node
        return compiled_node

    def compile_schema_dag(
        self,
        dag: SchemaDag,
        storage_manager: StorageManager,
    ) -> OnlineSchemaDag:
        compiled_nodes: list[OnlineNode] = [
            self.compile_node(node, storage_manager) for node in dag.nodes
        ]
        if not self.__store_compilation_results:
            self.__compiled_node_by_node_id = {}
        return OnlineSchemaDag(dag.schema, compiled_nodes)
