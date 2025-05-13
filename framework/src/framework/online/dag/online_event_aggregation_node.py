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

import itertools

from beartype.typing import Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.event_aggregator import (
    EventAggregator,
    EventAggregatorParams,
)
from superlinked.framework.online.dag.event_effect_handler import (
    EventAffectingInfo,
    EventEffectHandler,
)
from superlinked.framework.online.dag.event_metadata_handler import EventMetadataHandler
from superlinked.framework.online.dag.online_comparison_filter_node import (
    OnlineComparisonFilterNode,
)
from superlinked.framework.online.dag.online_node import OnlineNode


class OnlineEventAggregationNode(OnlineNode[EventAggregationNode, Vector], HasLength):
    def __init__(
        self,
        node: EventAggregationNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(node, parents, storage_manager)
        self.__init_named_parents()
        self._transformation_config = self.node.transformation_config
        self._event_metadata_handler = EventMetadataHandler(self.storage_manager, self.node.node_id)
        self._event_effect_handler = EventEffectHandler()

    def __init_named_parents(self) -> None:
        inputs_to_aggregate = [
            parent for parent in self.parents if parent.node.node_id == self.node.input_to_aggregate.node_id
        ]
        if len(inputs_to_aggregate) > 1:
            raise ParentCountException(
                f"{self.class_name} cannot have more than 1 parents to aggregate, got {len(inputs_to_aggregate)}"
            )
        self._input_to_aggregate = inputs_to_aggregate[0] if len(inputs_to_aggregate) > 0 else None
        self.weighted_filter_parents: dict[OnlineNode, float] = {
            parent: self.__get_parent_weight(parent)
            for parent in self.parents
            if isinstance(parent, OnlineComparisonFilterNode)
        }

    def __get_parent_weight(self, parent: OnlineNode) -> float:
        return next(
            (filter_.weight for filter_ in self.node.filters if filter_.item == parent.node),
            constants.DEFAULT_WEIGHT,
        )

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @override
    def evaluate_self(  # pylint: disable=too-many-locals  # we will refactor this
        self, parsed_schemas: Sequence[ParsedSchema], context: ExecutionContext
    ) -> list[EvaluationResult[Vector] | None]:
        if not parsed_schemas:
            return []
        parsed_schema_types = list({type(parsed_schema) for parsed_schema in parsed_schemas})
        if len(parsed_schema_types) != 1:
            raise NotImplementedError("Cannot process a mix of event and non-event parsed schemas.")
        unique_object_ids = list({parsed_schema.id_ for parsed_schema in parsed_schemas})
        schema = self.__get_single_schema(parsed_schemas)
        current_result_by_id = self._load_stored_result_by_id(schema, unique_object_ids)
        if self._input_to_aggregate is None or parsed_schema_types[0] != ParsedSchemaWithEvent:
            return self._to_evaluation_results(parsed_schemas, current_result_by_id)
        relevant_parsed_schemas = [
            parsed_schema
            for parsed_schema in cast(Sequence[ParsedSchemaWithEvent], parsed_schemas)
            if self.node.event_schema == parsed_schema.event_parsed_schema.schema
        ]

        remaining_ids = set(unique_object_ids)
        for _ in itertools.repeat(None, Settings().ONLINE_EVENT_AGGREGATION_NODE_MAX_RETRY_COUNT):
            if not remaining_ids:
                break
            object_id_to_metadata = self._event_metadata_handler.read(schema, list(remaining_ids))
            original_object_id_to_metadata = dict(object_id_to_metadata)
            parsed_schemas_to_process = [schema for schema in relevant_parsed_schemas if schema.id_ in remaining_ids]
            if not parsed_schemas_to_process:
                break
            event_id_to_affecting_info = self._calculate_event_id_to_affecting_info(
                context, parsed_schemas_to_process, self._input_to_aggregate
            )
            processed_ids = set()
            for parsed_schema in parsed_schemas_to_process:
                event_id = parsed_schema.event_parsed_schema.id_
                if event_id not in event_id_to_affecting_info:
                    continue
                object_id = parsed_schema.id_
                affecting_info = event_id_to_affecting_info[event_id]
                object_id_to_metadata[object_id] = self._event_metadata_handler.recalculate(
                    parsed_schema.event_parsed_schema.created_at,
                    affecting_info.number_of_weights,
                    object_id_to_metadata[object_id],
                )
                params = EventAggregatorParams(
                    context,
                    current_result_by_id[object_id],
                    Weighted(affecting_info.affecting_vector, affecting_info.average_weight),
                    object_id_to_metadata[object_id],
                    self.node.effect_modifier,
                    self._transformation_config,
                )
                current_result_by_id[object_id] = EventAggregator(params).calculate_event_vector()
                processed_ids.add(object_id)
            if not processed_ids:
                break
            current_metadata = self._event_metadata_handler.read(schema, list(processed_ids))
            conflicting_ids = {
                id_ for id_ in processed_ids if original_object_id_to_metadata.get(id_) != current_metadata.get(id_)
            }
            successful_ids = set(processed_ids) - conflicting_ids
            if successful_ids:
                self._event_metadata_handler.write(schema, {id_: object_id_to_metadata[id_] for id_ in successful_ids})
                remaining_ids -= successful_ids
        if remaining_ids:
            conflicting_metadata = {id_: object_id_to_metadata[id_] for id_ in remaining_ids}
            self._event_metadata_handler.write(schema, conflicting_metadata)
        return self._to_evaluation_results(parsed_schemas, current_result_by_id)

    def _to_evaluation_results(
        self, parsed_schemas: Sequence[ParsedSchema], current_result_by_id: Mapping[str, Vector]
    ) -> list[EvaluationResult[Vector] | None]:
        return [
            EvaluationResult(self._get_single_evaluation_result(current_result_by_id[parsed_schema.id_]))
            for parsed_schema in parsed_schemas
        ]

    def __get_single_schema(self, parsed_schemas: Sequence[ParsedSchema]) -> SchemaObject:
        for parsed_schema in parsed_schemas:
            if parsed_schema.schema != self.node.affected_schema.schema:
                raise ValidationException(
                    f"Unknown schema, {self.class_name} can only process"
                    + f" {self.node.affected_schema.schema._base_class_name} "
                    + f"got {parsed_schema.schema._base_class_name}"
                )
        return parsed_schemas[0].schema

    def _load_stored_result_by_id(self, schema: SchemaObject, object_ids: Sequence[str]) -> dict[str, Vector]:
        stored_results = self.load_stored_results([(schema, object_id) for object_id in object_ids])
        return {
            object_id: stored_result or Vector.empty_vector()
            for object_id, stored_result in zip(object_ids, stored_results)
        }

    def _calculate_event_id_to_affecting_info(
        self,
        context: ExecutionContext,
        parsed_schemas: Sequence[ParsedSchemaWithEvent],
        input_to_aggregate: OnlineNode,
    ) -> dict[str, EventAffectingInfo]:
        event_parsed_schemas = [parsed_schema.event_parsed_schema for parsed_schema in parsed_schemas]
        vectors = self._calculate_affecting_vectors(context, event_parsed_schemas, input_to_aggregate)
        weights = self._calculate_affecting_weights(context, event_parsed_schemas)
        return self._event_effect_handler.calculate_affecting_info_by_event_id(event_parsed_schemas, vectors, weights)

    def _calculate_affecting_vectors(
        self,
        context: ExecutionContext,
        event_parsed_schemas: Sequence[EventParsedSchema],
        input_to_aggregate: OnlineNode,
    ) -> list[Vector]:
        affecting_parsed_schemas = [
            self._event_effect_handler.map_event_schema_to_affecting_schema(
                self.node.affecting_schema, event_parsed_schema
            )
            for event_parsed_schema in event_parsed_schemas
        ]
        parent_results = self.evaluate_parent(input_to_aggregate, affecting_parsed_schemas, context)
        return [
            self._event_effect_handler.map_parent_result_to_vector(parent_result) for parent_result in parent_results
        ]

    def _calculate_affecting_weights(
        self,
        context: ExecutionContext,
        event_parsed_schemas: Sequence[EventParsedSchema],
    ) -> list[list[float]]:
        filter_parents = list(self.weighted_filter_parents.keys())
        parent_results = self.evaluate_parents(filter_parents, event_parsed_schemas, context)
        affecting_weights = [
            [self.weighted_filter_parents[parent] for parent, result in parent_result.items() if result.main.value]
            for parent_result in parent_results
        ]
        return affecting_weights
