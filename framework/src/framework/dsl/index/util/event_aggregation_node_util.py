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

from beartype.typing import cast

from superlinked.framework.common.dag.comparison_filter_node import ComparisonFilterNode
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.dag.schema_object_reference import (
    SchemaObjectReference,
)
from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.index.effect import EffectModifier
from superlinked.framework.dsl.index.util.effect_with_referenced_schema_object import (
    EffectWithReferencedSchemaObject,
)
from superlinked.framework.dsl.index.util.event_aggregation_effect_group import (
    EventAggregationEffectGroup,
)


class EventAggregationNodeUtil:
    @staticmethod
    def init_event_aggregation_node(
        effect_group: EventAggregationEffectGroup,
        effect_modifier: EffectModifier,
    ) -> EventAggregationNode:
        if not effect_group.effects:
            raise InitializationException(
                "EventAggregationNode initialization needs a not empty set of Effects."
            )

        return EventAggregationNode(
            EventAggregationNode.InitParams(
                effect_group.key.space._get_node(
                    effect_group.key.resolved_affecting_schema
                ),
                effect_group.key.event_schema,
                SchemaObjectReference(
                    effect_group.key.resolved_affected_schema_reference.schema,
                    effect_group.key.resolved_affected_schema_reference.reference_field,
                ),
                SchemaObjectReference(
                    effect_group.key.resolved_affecting_schema,
                    effect_group.key.resolved_affecting_reference_field,
                ),
                EventAggregationNodeUtil.__create_filter_nodes(effect_group.effects),
                {effect.dag_effect for effect in effect_group.effects},
                effect_modifier,
            )
        )

    @staticmethod
    def __create_filter_nodes(
        effects: list[EffectWithReferencedSchemaObject],
    ) -> list[Weighted[ComparisonFilterNode]]:
        return [
            Weighted(
                ComparisonFilterNode(
                    SchemaFieldNode(
                        cast(SchemaField, effect.base_effect.filter_._operand),
                        {effect.dag_effect for effect in effects},
                    ),
                    effect.base_effect.filter_,
                    {effect.dag_effect},
                ),
                effect.dag_effect.resolved_affecting_schema_reference.multiplier,
            )
            for effect in effects
        ]
