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
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResultT,
)
from superlinked.framework.query.dag.query_node_with_parent import QueryNodeWithParent
from superlinked.framework.query.query_node_input import (
    QueryNodeInput,
    QueryNodeInputValue,
)


class InvertIfAddressedQueryNode(
    QueryNodeWithParent[NT, QueryEvaluationResultT],
    ABC,
    Generic[NT, QueryEvaluationResultT],
):
    @override
    def _propagate_inputs_to_invert(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> dict[str, Sequence[QueryNodeInput]]:
        inputs_to_invert = [input_.value for input_ in inputs.get(self.node_id, []) if input_.to_invert]
        inverted_inputs = self._invert_and_readdress(inputs_to_invert)
        new_inputs = self._merge_inputs([inputs, inverted_inputs])
        return new_inputs

    @abstractmethod
    def _invert_and_readdress(self, node_inputs: Sequence[QueryNodeInputValue]) -> dict[str, list[QueryNodeInput]]:
        pass
