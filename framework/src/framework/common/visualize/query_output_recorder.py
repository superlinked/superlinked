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


from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.visualize.output_recorder import OutputRecorder
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)


class QueryOutputRecorder(OutputRecorder[QueryEvaluationResult]):
    @property
    @override
    def _id(self) -> str:
        return "query"

    @override
    def _map_output_to_data_to_be_visualized(self, output: QueryEvaluationResult) -> Any:
        return output.value
