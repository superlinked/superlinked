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
from contextlib import contextmanager

from beartype.typing import Any, Generator, Generic, Mapping, Sequence, TypeVar

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.visualize.dag_visualizer import DagVisualizer
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)

OutputTypes = Mapping[str, Any] | EvaluationResult | QueryEvaluationResult | None
OutputT = TypeVar("OutputT", bound=OutputTypes)


class OutputRecorder(Generic[OutputT], ABC):
    def __init__(self) -> None:
        self.__node_outputs = dict[str, Sequence[OutputT] | Exception]()
        self.__dag_visualizer = DagVisualizer(self._id)

    @contextmanager
    def record_evaluation_exception(self, node_id: str) -> Generator[None, Any, None]:
        try:
            yield
        except Exception as e:
            self.record(node_id, e)
            raise

    @contextmanager
    def visualize_dag_context(self, nodes: Sequence[Node]) -> Generator[None, Any, None]:
        try:
            yield
        except Exception:
            self.visualize(nodes)
            raise
        self.visualize(nodes)

    def record(self, node_id: str, output: Sequence[OutputT] | Exception) -> None:
        self.__node_outputs[node_id] = output

    def visualize(self, nodes: Sequence[Node]) -> None:
        mapped_outputs = self.__get_outputs_as_node_data_types()
        self.__dag_visualizer.visualize_evaluation(nodes, mapped_outputs)

    @property
    @abstractmethod
    def _id(self) -> str: ...

    @abstractmethod
    def _map_output_to_data_to_be_visualized(self, output: OutputT) -> Any: ...

    @property
    def _node_outputs(self) -> Mapping[str, Sequence[OutputT] | Exception]:
        return self.__node_outputs

    def __get_outputs_as_node_data_types(self) -> Mapping[str, Sequence[NodeDataTypes] | Exception]:
        return {
            node_id: (
                node_results
                if isinstance(node_results, Exception)
                else [self._map_output_to_data_to_be_visualized(node_result) for node_result in node_results]
            )
            for node_id, node_results in self._node_outputs.items()
            if node_results is not None
        }
