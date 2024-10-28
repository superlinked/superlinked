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

from abc import ABC, abstractmethod

from beartype.typing import Generic, Mapping, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NT
from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
    QueryEvaluationResultT,
)
from superlinked.framework.query.dag.query_node_with_parent import QueryNodeWithParent
from superlinked.framework.query.query_node_input import QueryNodeInput


class InvertIfAddressedQueryNode(
    QueryNodeWithParent[NT, QueryEvaluationResultT],
    ABC,
    Generic[NT, QueryEvaluationResultT],
):
    @override
    def _evaluate_parents(
        self, inputs: Mapping[str, Sequence[QueryNodeInput]], context: ExecutionContext
    ) -> list[QueryEvaluationResult]:
        node_inputs: list[Weighted[NodeDataTypes]] = [
            node_input.value for node_input in inputs.get(self.node_id, [])
        ]
        inverted_inputs = self.invert_and_readdress(node_inputs)
        new_inputs = self._merge_inputs([inputs, inverted_inputs])
        return super()._evaluate_parents(new_inputs, context)

    @abstractmethod
    def invert_and_readdress(
        self, node_inputs: Sequence[Weighted[NodeDataTypes]]
    ) -> dict[str, list[QueryNodeInput]]:
        pass
