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

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.exception import InvalidDagEffectException
from superlinked.framework.common.observable import Subscriber
from superlinked.framework.common.parser.exception import MissingFieldException
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.online.online_dag_evaluator import OnlineDagEvaluator

logger = structlog.get_logger()


class OnlineDataProcessor(Subscriber[ParsedSchema]):
    MAX_SAVE_DEPTH = 10

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

    def _init_mandatory_field_names_by_schema(
        self, index: Index
    ) -> defaultdict[SchemaObject, list[str]]:
        mandatory_field_names_by_schema: defaultdict[SchemaObject, list[str]] = (
            defaultdict(list)
        )
        for field in index._fields:
            mandatory_field_names_by_schema[field.schema_obj].append(field.name)
        return mandatory_field_names_by_schema

    def update(self, messages: Sequence[ParsedSchema]) -> None:
        regular_msgs: list[ParsedSchema] = []
        for message in messages:
            self._validate_mandatory_fields_are_present(message)
        for message in messages:
            if message.schema in self.effect_schemas:
                self._process_event(cast(EventParsedSchema, message))
            else:
                regular_msgs.append(message)
        if regular_msgs:
            for parsed_schema in regular_msgs:
                self.storage_manager.write_parsed_schema_fields(
                    parsed_schema.id_, parsed_schema.fields
                )
            self.evaluator.evaluate(regular_msgs, self.context)

        logger.info(
            "stored input data",
            schemas=list(
                {parsed_schema.schema._schema_name for parsed_schema in messages}
            ),
            n_records=len(messages),
        )

    def _validate_mandatory_fields_are_present(self, message: ParsedSchema) -> None:
        field_names = [field.schema_field.name for field in message.fields]
        missing_fields = [
            field_name
            for field_name in self._mandatory_field_names_by_schema.get(
                message.schema, []
            )
            if field_name not in field_names
        ]
        if missing_fields:
            missing_fields_text = ", ".join(missing_fields)
            raise MissingFieldException(
                f"Message with id '{message.id_}' is missing mandatory index fields: {missing_fields_text}."
            )

    def _process_event(
        self,
        event_parsed_schema: EventParsedSchema,
    ) -> None:
        effect_parsed_schema_map = self._map_event_parsed_schema_by_dag_effects(
            event_parsed_schema
        )
        for effect, parsed_schema_with_event in effect_parsed_schema_map.items():
            self.evaluator.evaluate_by_dag_effect(
                parsed_schema_with_event, self.context, effect
            )

    def _map_event_parsed_schema_by_dag_effects(
        self, event_parsed_schema: EventParsedSchema
    ) -> dict[DagEffect, ParsedSchemaWithEvent]:
        effects_with_schema_matching = [
            effect
            for effect in self._dag_effects
            if effect.event_schema == event_parsed_schema.schema
        ]
        effects_with_all_matching_except_multiplier = [
            effect
            for i, effect in enumerate(effects_with_schema_matching)
            if not any(
                effect.is_same_effect_except_for_multiplier(other_effect)
                for other_effect in effects_with_schema_matching[:i]
            )
        ]
        effect_parsed_schema_map = dict[DagEffect, ParsedSchemaWithEvent]()
        for effect in effects_with_all_matching_except_multiplier:
            affected_schema_ids = [
                reference.value
                for reference in event_parsed_schema.fields
                if reference.schema_field
                == effect.resolved_affected_schema_reference.reference_field
                and reference.value is not None
            ]
            if len(affected_schema_ids) > 1:
                raise InvalidDagEffectException(f"DagEffect: {effect}")
            if affected_schema_ids:
                effect_parsed_schema_map[effect] = ParsedSchemaWithEvent(
                    effect.resolved_affected_schema_reference.schema,
                    affected_schema_ids[0],
                    [],
                    event_parsed_schema,
                )
        return effect_parsed_schema_map
