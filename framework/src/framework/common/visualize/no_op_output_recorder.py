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


from beartype.typing import Any, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.visualize.output_recorder import OutputRecorder


class NoOpOutputRecorder(OutputRecorder[Any]):
    @property
    @override
    def _id(self) -> str:
        return "does_nothing"

    @override
    def _map_output_to_data_to_be_visualized(self, output: Any) -> Any:
        return output

    @override
    def visualize(self, nodes: Sequence[Node]) -> None:
        pass

    @override
    def record(self, node_id: str, output: Sequence[Any] | Exception) -> None:
        pass
