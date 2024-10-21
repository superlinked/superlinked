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

from beartype.typing import Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.aggregation.aggregation import Aggregation
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.transform.transform import Step


class AggregationStep(
    Generic[AggregationInputT],
    Step[Sequence[Weighted[AggregationInputT]], AggregationInputT],
):
    def __init__(
        self,
        aggregation: Aggregation[AggregationInputT],
    ) -> None:
        super().__init__()
        self._aggregation = aggregation

    @override
    def transform(
        self,
        input_: Sequence[Weighted[AggregationInputT]],
        context: ExecutionContext,
    ) -> AggregationInputT:
        return self._aggregation.aggregate_weighted(input_, context)
