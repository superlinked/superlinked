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

from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.dsl.index.util.effect_with_referenced_schema_object import (
    EffectWithReferencedSchemaObject,
)
from superlinked.framework.dsl.space.space import Space


@dataclass
class AggregationEffectGroup:
    """
    Group of effects with the same space and affected schema.
    """

    space: Space
    affected_schema: SchemaObject
    effects: list[EffectWithReferencedSchemaObject]

    @classmethod
    def from_filtered_effects(
        cls,
        filtered_effects: list[EffectWithReferencedSchemaObject],
    ) -> AggregationEffectGroup:
        effect_sample = filtered_effects[0]
        return cls(
            effect_sample.base_effect.space,
            effect_sample.resolved_affected_schema_reference.schema,
            filtered_effects,
        )
