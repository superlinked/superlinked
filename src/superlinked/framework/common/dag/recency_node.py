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
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.recency_embedding import RecencyEmbedding
from superlinked.framework.common.interface.has_length import HasLength


class RecencyNode(Node[Vector], HasLength):
    def __init__(
        self,
        parent: Node[int],
        period_time_list: list[PeriodTime],
        negative_filter: float = 0.0,
    ) -> None:
        super().__init__([parent])
        self.embedding: RecencyEmbedding = RecencyEmbedding(
            period_time_list=period_time_list,
            negative_filter=negative_filter,
        )

    @property
    def length(self) -> int:
        return self.embedding.length
