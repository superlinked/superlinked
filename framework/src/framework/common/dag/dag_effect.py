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

from superlinked.framework.common.dag.resolved_schema_reference import (
    ResolvedSchemaReference,
)
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject


@dataclass(frozen=True)
class DagEffect:
    resolved_affected_schema_reference: ResolvedSchemaReference
    resolved_affecting_schema_reference: ResolvedSchemaReference
    event_schema: EventSchemaObject

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(resolved_affected_schema_reference={self.resolved_affected_schema_reference}, "
            f"resolved_affecting_schema_reference={self.resolved_affecting_schema_reference}, "
            f"event_schema={self.event_schema._schema_name})"
        )

    def is_same_effect_except_for_multiplier(self, other: DagEffect) -> bool:
        if other == self:
            return True
        return bool(
            self.resolved_affected_schema_reference == other.resolved_affected_schema_reference
            and self.event_schema == other.event_schema
            and self.resolved_affecting_schema_reference.reference_field
            == other.resolved_affecting_schema_reference.reference_field
            and self.resolved_affecting_schema_reference.schema == other.resolved_affecting_schema_reference.schema
        )
