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

from collections import defaultdict

import structlog
from beartype.typing import Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.resolved_schema_reference import (
    ResolvedSchemaReference,
)
from superlinked.framework.common.exception import InvalidDagEffectException
from superlinked.framework.common.observable import Subscriber
from superlinked.framework.common.parser.exception import MissingFieldException
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.settings import settings
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.util.concurrent_executor import ConcurrentExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.online.dag_effect_group import DagEffectGroup
from superlinked.framework.online.online_dag_evaluator import OnlineDagEvaluator

logger = structlog.get_logger()


class OnlineDataProcessor(Subscriber[ParsedSchema]):
    def __init__(
        self,
        evaluator: OnlineDagEvaluator,
        storage_manager: StorageManager,
        context: ExecutionContext,
        index: Index,
    ) -> None:
        super().__init__()
        self.evaluator = evaluator
        self.context = context
        self.storage_manager = storage_manager
        self.effect_schemas = set(index._effect_schemas)
        self._schema_type_schema_mapper = index._schema_type_schema_mapper
        self._dag_effects = index._dag_effects
        self._mandatory_field_names_by_schema: Mapping[SchemaObject, Sequence[str]] = (
            self._init_mandatory_field_names_by_schema(index)
        )

    def _init_mandatory_field_names_by_schema(self, index: Index) -> defaultdict[SchemaObject, list[str]]:
        mandatory_field_names_by_schema: defaultdict[SchemaObject, list[str]] = defaultdict(list)
        id_field_names_by_schema: dict[SchemaObject, str] = {
            schema: schema.id.name for schema in index.schemas if isinstance(schema, IdSchemaObject)
        }
        for field in index.non_nullable_fields:
            field_name = field.name
            field_schema = field.schema_obj
            if id_field_names_by_schema[field_schema] != field_name:
                mandatory_field_names_by_schema[field_schema].append(field_name)
        return mandatory_field_names_by_schema

    @override
    def update(self, messages: Sequence[ParsedSchema]) -> None:
        for message in messages:
            self._validate_mandatory_fields_are_present(message)
        event_msgs = list[EventParsedSchema]()
        regular_msgs = list[ParsedSchema]()
        for message in messages:
            if message.schema in self.effect_schemas:
                event_msgs.append(cast(EventParsedSchema, message))
            else:
                regular_msgs.append(message)
        if regular_msgs:
            self.storage_manager.write_parsed_schema_fields(regular_msgs)
            self.evaluator.evaluate(regular_msgs, self.context)

        if event_msgs:
            self._process_events(event_msgs)
        logger.info(
            "stored input data",
            schemas=list({parsed_schema.schema._schema_name for parsed_schema in messages}),
            n_records=len(messages),
        )

    def _validate_mandatory_fields_are_present(self, message: ParsedSchema) -> None:
        field_names = [field.schema_field.name for field in message.fields if field.value is not None]
        missing_fields = [
            field_name
            for field_name in self._mandatory_field_names_by_schema.get(message.schema, [])
            if field_name not in field_names
        ]
        if missing_fields:
            missing_fields_text = ", ".join(missing_fields)
            raise MissingFieldException(
                f"Message with id '{message.id_}' is missing mandatory index fields: {missing_fields_text}."
            )

    def _process_events(self, event_parsed_schemas: Sequence[EventParsedSchema]) -> None:
        effects_to_parsed_schemas = self._map_effects_to_parsed_schemas(event_parsed_schemas)
        effect_groups_to_parsed_schemas = self._map_effect_groups_to_parsed_schemas(effects_to_parsed_schemas)
        execution_args = [
            (parsed_schemas, self.context, effect_group)
            for effect_group, parsed_schemas in effect_groups_to_parsed_schemas.items()
        ]
        ConcurrentExecutor().execute(
            func=self.evaluator.evaluate_by_dag_effect_group,
            args_list=execution_args,
            condition=settings.SUPERLINKED_CONCURRENT_EFFECT_EVALUATION,
        )

    def _map_effects_to_parsed_schemas(
        self, event_parsed_schemas: Sequence[EventParsedSchema]
    ) -> dict[DagEffect, list[ParsedSchemaWithEvent]]:
        effects_to_parsed_schemas: dict[DagEffect, list[ParsedSchemaWithEvent]] = defaultdict(list)
        for event_parsed_schema in event_parsed_schemas:
            for effect in self._get_matching_effects(event_parsed_schema):
                if schema_with_event := self._create_parsed_schema_with_event(
                    effect.resolved_affected_schema_reference, event_parsed_schema
                ):
                    effects_to_parsed_schemas[effect].append(schema_with_event)
        return effects_to_parsed_schemas

    def _get_matching_effects(self, event_schema: EventParsedSchema) -> list[DagEffect]:
        return [effect for effect in self._dag_effects if effect.event_schema == event_schema.schema]

    def _map_effect_groups_to_parsed_schemas(
        self, effects_to_parsed_schemas: Mapping[DagEffect, Sequence[ParsedSchemaWithEvent]]
    ) -> dict[DagEffectGroup, list[ParsedSchemaWithEvent]]:
        effect_groups_to_parsed_schemas: dict[DagEffectGroup, list[ParsedSchemaWithEvent]] = defaultdict(list)
        for effect, parsed_schemas in effects_to_parsed_schemas.items():
            effect_group = self.evaluator.effect_to_group[effect]
            effect_groups_to_parsed_schemas[effect_group].extend(parsed_schemas)
        return dict(effect_groups_to_parsed_schemas)

    def _create_parsed_schema_with_event(
        self,
        affected_schema_reference: ResolvedSchemaReference,
        event_parsed_schema: EventParsedSchema,
    ) -> ParsedSchemaWithEvent | None:
        affected_schema_ids = [
            reference.value
            for reference in event_parsed_schema.fields
            if reference.schema_field == affected_schema_reference.reference_field and reference.value is not None
        ]
        if not affected_schema_ids:
            return None

        if len(affected_schema_ids) > 1:
            raise InvalidDagEffectException(f"Affected schema reference: {affected_schema_reference}")
        return ParsedSchemaWithEvent(affected_schema_reference.schema, affected_schema_ids[0], [], event_parsed_schema)
