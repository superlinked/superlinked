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

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

from superlinked.framework.common.dag.resolved_schema_reference import (
    ResolvedSchemaReference,
)
from superlinked.framework.common.schema.event_schema_object import (
    EventSchemaObject,
    SchemaReference,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.dsl.index.util.effect_with_referenced_schema_object import (
    EffectWithReferencedSchemaObject,
)
from superlinked.framework.dsl.space.space import Space


@dataclass
class EventAggregationEffectGroup:
    """
    Group of effects with the same space, event schema, affected schema and affecting schema.
    """

    @dataclass(frozen=True)
    class GroupKey:
        space: Space
        event_schema: EventSchemaObject
        resolved_affected_schema_reference: ResolvedSchemaReference
        resolved_affecting_schema: IdSchemaObject
        resolved_affecting_reference_field: SchemaReference

    key: GroupKey
    effects: list[EffectWithReferencedSchemaObject]

    @classmethod
    def group_by_event_and_affecting_schema(
        cls, effects: list[EffectWithReferencedSchemaObject]
    ) -> list[EventAggregationEffectGroup]:
        return [
            cls(
                group_key,
                list(effect_group),
            )
            for group_key, effect_group in groupby(
                sorted(effects, key=EventAggregationEffectGroup.__get_group_key_hash),
                EventAggregationEffectGroup.__get_group_key,
            )
        ]

    @staticmethod
    def __get_group_key(effect_: EffectWithReferencedSchemaObject) -> GroupKey:
        return EventAggregationEffectGroup.GroupKey(
            effect_.base_effect.space,
            effect_.event_schema,
            effect_.resolved_affected_schema_reference,
            effect_.resolved_affecting_schema_reference.schema,
            effect_.resolved_affecting_schema_reference.reference_field,
        )

    @staticmethod
    def __get_group_key_hash(effect_: EffectWithReferencedSchemaObject) -> int:
        return hash(EventAggregationEffectGroup.__get_group_key(effect_))
