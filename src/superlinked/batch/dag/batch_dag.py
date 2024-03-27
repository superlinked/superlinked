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

from typing import Mapping

from superlinked.batch.dag.batch_node import BatchNode
from superlinked.framework.common.dag.node import Node


class BatchDag:
    """
    Represents a `BatchDag`. Not currently used.
    """

    def __init__(
        self,
        nodes: Mapping[Node, BatchNode],
        index_nodes: list[Node],
    ) -> None:
        self.__nodes = nodes
        self.__index_nodes = index_nodes

    @property
    def nodes(self) -> Mapping[Node, BatchNode]:
        return self.__nodes
