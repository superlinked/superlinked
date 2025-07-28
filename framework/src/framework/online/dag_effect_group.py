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

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject


@dataclass(frozen=True)
class DagEffectGroup:
    """
    Represents a group of effects that are identical except for their multipliers to avoid concurrency problems
    during the evaluation of online event DAGs. Effects that are the same except for the multiplier
    would otherwise cause race conditions when processed concurrently
    by updating the stored result and metadata values of the OEAN potentially at the same time.
    """

    effects: frozenset[DagEffect]

    def __post_init__(self) -> None:
        if len(self.effects) == 0:
            raise InvalidStateException("DagEffectGroup must contain at least one effect")
        first = next(iter(self.effects))
        for effect in self.effects:
            if not first.is_same_effect_except_for_multiplier(effect):
                raise InvalidStateException(
                    "All effects in a DagEffectGroup must be identical except for their multipliers"
                )

    @property
    def affected_schema(self) -> IdSchemaObject:
        return next(iter(self.effects)).resolved_affected_schema_reference.schema

    @property
    def affecting_schema(self) -> IdSchemaObject:
        return next(iter(self.effects)).resolved_affecting_schema_reference.schema

    @property
    def event_schema(self) -> EventSchemaObject:
        return next(iter(self.effects)).event_schema

    @classmethod
    def group_similar_effects(cls, dag_effects: set[DagEffect]) -> list[DagEffectGroup]:
        result = []
        unprocessed_effects = set(dag_effects)
        while unprocessed_effects:
            effect = next(iter(unprocessed_effects))
            similar_effects = {
                other for other in unprocessed_effects if effect.is_same_effect_except_for_multiplier(other)
            }
            unprocessed_effects.difference_update(similar_effects)
            result.append(cls(frozenset(similar_effects)))
        return result
