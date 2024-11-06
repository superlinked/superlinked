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


from dataclasses import asdict

from beartype.typing import Any, Generic, TypeVar
from typing_extensions import override

from superlinked.framework.common.dag.node import Node, NodeDataT
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.space.interface.has_transformation_config import (
    HasTransformationConfig,
)


class EmbeddingNode(
    Generic[AggregationInputT, NodeDataT],
    Node[Vector],
    HasTransformationConfig[AggregationInputT, NodeDataT],
):
    def __init__(
        self,
        parents: list[Node],
        transformation_config: TransformationConfig[AggregationInputT, NodeDataT],
    ) -> None:
        super().__init__(Vector, parents)
        self._transformation_config = transformation_config

    @property
    @override
    def length(self) -> int:
        return self._transformation_config.length

    @property
    @override
    def transformation_config(
        self,
    ) -> TransformationConfig[AggregationInputT, NodeDataT]:
        return self._transformation_config

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "transformation_config": asdict(self.transformation_config),
        }


EmbeddingNodeT = TypeVar("EmbeddingNodeT", bound=EmbeddingNode)
