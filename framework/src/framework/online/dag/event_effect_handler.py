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

from beartype.typing import Any, Sequence

from superlinked.framework.common.dag.schema_object_reference import (
    SchemaObjectReference,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import DagEvaluationException
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
)
from superlinked.framework.online.dag.evaluation_result import EvaluationResult


@dataclass(frozen=True)
class EventAffectingInfo:
    affecting_vector: Vector
    number_of_weights: int
    average_weight: float


class EventEffectHandler:

    def calculate_affecting_info_by_event_id(
        self,
        event_parsed_schemas: Sequence[EventParsedSchema],
        affecting_vectors: Sequence[Vector],
        affecting_weights: Sequence[Sequence[float]],
    ) -> dict[str, EventAffectingInfo]:
        if len(event_parsed_schemas) != len(affecting_vectors) or len(event_parsed_schemas) != len(affecting_weights):
            raise DagEvaluationException(
                f"Input sequences must have the same length. Got: {len(event_parsed_schemas)} event_parsed_schemas, "
                f"{len(affecting_vectors)} affecting_vectors, and {len(affecting_weights)} affecting_weights."
            )
        return {
            event_parsed_schema.id_: EventAffectingInfo(vector, len(weights), sum(weights) / len(weights))
            for event_parsed_schema, vector, weights in zip(event_parsed_schemas, affecting_vectors, affecting_weights)
            if self._should_process_event(vector, weights)
        }

    def _should_process_event(self, affecting_vector: Vector, weights: Sequence[float]) -> bool:
        """
        For 2 event effects on different spaces and/or of different EventSchemas
        and/or on different affected schemas, 2 OnlineEventAggregationNode (OEAN) will be created.
        When receiving an event, both OEANs will be evaluated. The `weights`
        variable will be empty for one of them since the event only affects one space.
        In this case, we should return the stored result since the weight would be 0.
        Also when affecting_vector.is_empty, then it will not have any affect.
        """
        return len(weights) > 0 and not affecting_vector.is_empty

    def map_parent_result_to_vector(self, parent_result: EvaluationResult[Any] | None) -> Vector:
        if parent_result is None:
            raise DagEvaluationException("OEAN parent_to_aggregate's evaluation result cannot be None")
        vector = parent_result.main.value
        if not isinstance(vector, Vector):
            raise DagEvaluationException(
                f"parent_to_aggregate's evaluation result must be of type Vector, got {type(vector).__name__}"
            )
        return vector

    def map_event_schema_to_affecting_schema(
        self, affecting_schema: SchemaObjectReference, event_parsed_schema: EventParsedSchema
    ) -> ParsedSchema:
        return next(
            ParsedSchema(affecting_schema.schema, field.value, [])
            for field in event_parsed_schema.fields
            if field.schema_field == affecting_schema.reference_field
        )
