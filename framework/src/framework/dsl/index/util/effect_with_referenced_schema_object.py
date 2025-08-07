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

from beartype.typing import Generic, cast

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.resolved_schema_reference import (
    ResolvedSchemaReference,
)
from superlinked.framework.common.exception import (
    InvalidInputException,
    InvalidStateException,
)
from superlinked.framework.common.schema.event_schema_object import (
    EventSchemaObject,
    MultipliedSchemaReference,
    SchemaReference,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingInputT,
)
from superlinked.framework.dsl.index.effect import Effect


@dataclass(frozen=True)
class EffectWithReferencedSchemaObject(Generic[AggregationInputT, EmbeddingInputT]):
    base_effect: Effect[AggregationInputT, EmbeddingInputT]
    resolved_affected_schema_reference: ResolvedSchemaReference
    resolved_affecting_schema_reference: ResolvedSchemaReference
    event_schema: EventSchemaObject

    @property
    def dag_effect(self) -> DagEffect:
        return DagEffect(
            self.resolved_affected_schema_reference,
            self.resolved_affecting_schema_reference,
            self.event_schema,
        )

    @classmethod
    def from_base_effect(cls, base_effect: Effect, schemas: set[IdSchemaObject]) -> EffectWithReferencedSchemaObject:
        (
            resolved_affected_schema_reference,
            resolved_affecting_schema_reference,
        ) = EffectWithReferencedSchemaObject._init_resolved_schema_reference_fields(base_effect, schemas)
        event_schema = EffectWithReferencedSchemaObject._get_event_schema(
            resolved_affected_schema_reference,
            resolved_affecting_schema_reference,
        )
        return cls(
            base_effect,
            resolved_affected_schema_reference,
            resolved_affecting_schema_reference,
            event_schema,
        )

    @staticmethod
    def _init_resolved_schema_reference_fields(
        effect: Effect, schemas: set[IdSchemaObject]
    ) -> tuple[ResolvedSchemaReference, ResolvedSchemaReference]:
        resolved_affected_schema_reference = EffectWithReferencedSchemaObject._get_resolved_schema_reference(
            effect.affected_schema_reference, schemas
        )
        resolved_affecting_schema_reference = EffectWithReferencedSchemaObject._get_resolved_schema_reference(
            effect.affecting_schema_reference,
            schemas,
        )
        return (resolved_affected_schema_reference, resolved_affecting_schema_reference)

    @staticmethod
    def _get_event_schema(
        resolved_affected_schema_reference: ResolvedSchemaReference,
        resolved_affecting_schema_reference: ResolvedSchemaReference,
    ) -> EventSchemaObject:
        if (
            resolved_affected_schema_reference.reference_field.schema_obj
            != resolved_affecting_schema_reference.reference_field.schema_obj
        ):

            raise InvalidStateException(
                "An Effect's affected and affecting schema reference must come from the same EventSchema.",
                affected_reference_schema=resolved_affected_schema_reference.reference_field.schema_obj._schema_name,
                affecting_reference_schema=resolved_affecting_schema_reference.reference_field.schema_obj._schema_name,
            )
        return cast(
            EventSchemaObject,
            resolved_affected_schema_reference.reference_field.schema_obj,
        )

    @staticmethod
    def _get_resolved_schema_reference(
        unchecked_schema_reference: SchemaReference | MultipliedSchemaReference,
        schemas: set[IdSchemaObject],
    ) -> ResolvedSchemaReference:
        (
            schema_reference,
            reference_multiplier,
        ) = EffectWithReferencedSchemaObject._get_reference_and_multiplier(unchecked_schema_reference)
        schema = EffectWithReferencedSchemaObject._get_schema_object_for_reference(schema_reference, schemas)
        return ResolvedSchemaReference(
            schema,
            schema_reference,
            reference_multiplier,
        )

    @staticmethod
    def _get_reference_and_multiplier(
        unchecked_schema_reference: SchemaReference | MultipliedSchemaReference,
    ) -> tuple[SchemaReference, float]:
        result_schema_reference = (
            unchecked_schema_reference.schema_reference
            if isinstance(unchecked_schema_reference, MultipliedSchemaReference)
            else unchecked_schema_reference
        )
        multiplier = unchecked_schema_reference.multiplier
        if multiplier == 0:
            raise InvalidInputException("SchemaReference cannot have 0 (zero) as its multiplier.")
        return (result_schema_reference, multiplier)

    @staticmethod
    def _get_schema_object_for_reference(
        schema_reference: SchemaReference, schemas: set[IdSchemaObject]
    ) -> IdSchemaObject:
        schema_ = next(
            (schema_ for schema_ in schemas if isinstance(schema_, schema_reference._referenced_schema)),
            None,
        )
        if schema_ is None:
            schemas_as_text = ", ".join(schema._schema_name for schema in schemas)
            raise InvalidInputException(
                f"Referenced schema type `{schema_reference.name}` is"
                + f" not present in the index schemas: {schemas_as_text}"
            )
        return schema_
