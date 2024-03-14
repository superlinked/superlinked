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

from typing import cast

from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.dsl.index.util.aggregation_effect_group import (
    AggregationEffectGroup,
)
from superlinked.framework.dsl.index.util.event_aggregation_effect_group import (
    EventAggregationEffectGroup,
)
from superlinked.framework.dsl.index.util.event_aggregation_node_util import (
    EventAggregationNodeUtil,
)


class AggregationNodeUtil:
    @staticmethod
    def init_aggregation_node(
        aggregation_effect_group: AggregationEffectGroup,
    ) -> AggregationNode:
        if len(aggregation_effect_group.effects) == 0:
            raise InitializationException(
                "AggregationNode initialization needs a non-empty set of Effects."
            )
        event_aggregation_effect_groups = (
            EventAggregationEffectGroup.group_by_event_and_affecting_schema(
                aggregation_effect_group.effects
            )
        )
        eans = [
            EventAggregationNodeUtil.init_event_aggregation_node(eg)
            for eg in event_aggregation_effect_groups
        ]
        aggregation_node = AggregationNode(
            [
                Weighted(cast(Node[Vector], parent))
                for parent in eans
                + [
                    aggregation_effect_group.space._get_node(
                        aggregation_effect_group.affected_schema
                    )
                ]
            ],
            {effect.dag_effect for effect in aggregation_effect_group.effects},
        )
        return aggregation_node
