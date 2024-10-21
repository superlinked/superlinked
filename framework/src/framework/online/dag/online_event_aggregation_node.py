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

import math

from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    DagEvaluationException,
    ValidationException,
)
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.event_aggregator import (
    EventAggregator,
    EventAggregatorParams,
    EventMetadata,
)
from superlinked.framework.online.dag.online_comparison_filter_node import (
    OnlineComparisonFilterNode,
)
from superlinked.framework.online.dag.online_node import OnlineNode


class OnlineEventAggregationNode(OnlineNode[EventAggregationNode, Vector], HasLength):
    EFFECT_COUNT_KEY = "effect_count"
    EFFECT_OLDEST_TS_KEY = "effect_oldest_age"
    EFFECT_AVG_TS_KEY = "average_age"

    def __init__(
        self,
        node: EventAggregationNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(node, parents, storage_manager)
        self.__init_named_parents()
        # in case 2 effects are identical except for the multiplier
        self._metadata_key = str(self.node.effect_modifier)
        self._transformation_config = self.node.transformation_config

    def __init_named_parents(self) -> None:
        inputs_to_aggregate = [
            parent
            for parent in self.parents
            if parent.node.node_id == self.node.input_to_aggregate.node_id
        ]
        if len(inputs_to_aggregate) > 1:
            raise ParentCountException(
                f"{self.class_name} cannot have more than 1 parents to aggregate, got {len(inputs_to_aggregate)}"
            )
        self._input_to_aggregate = (
            inputs_to_aggregate[0] if len(inputs_to_aggregate) > 0 else None
        )
        self.weighted_filter_parents = {
            parent: self.__get_parent_weight(parent)
            for parent in self.parents
            if isinstance(parent, OnlineComparisonFilterNode)
        }

    def __get_parent_weight(self, parent: OnlineNode) -> float:
        return next(
            (
                filter_.weight
                for filter_ in self.node.filters
                if filter_.item == parent.node
            ),
            constants.DEFAULT_WEIGHT,
        )

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @override
    def evaluate_self(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[Vector]]:
        return [self.evaluate_self_single(schema, context) for schema in parsed_schemas]

    def evaluate_self_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[Vector]:
        self.__check_schema_validity(parsed_schema.schema)
        stored_result = (
            self.load_stored_result(parsed_schema.id_, parsed_schema.schema)
            or Vector.empty_vector()
        )
        input_to_aggregate = self._input_to_aggregate
        if (
            not isinstance(parsed_schema, ParsedSchemaWithEvent)
            or self.node.event_schema != parsed_schema.event_parsed_schema.schema
            or input_to_aggregate is None
        ):
            return EvaluationResult(self._get_single_evaluation_result(stored_result))

        affecting_vector = self._calculate_affecting_vector(
            context, parsed_schema.event_parsed_schema, input_to_aggregate
        )
        weights = self._calculate_affecting_weights(
            parsed_schema.event_parsed_schema, context
        )
        avg_affecting_weight = (
            (sum(weights) / len(weights)) if not affecting_vector.is_empty else 0
        )
        event_metadata: EventMetadata = self._calculate_and_store_metadata(
            parsed_schema, len(weights)
        )
        event_aggregator_params = EventAggregatorParams(
            context,
            stored_result,
            Weighted(affecting_vector, avg_affecting_weight),
            event_metadata,
            self.node.effect_modifier,
            self._transformation_config,
        )
        event_vector = EventAggregator(event_aggregator_params).calculate_event_vector()
        return EvaluationResult(self._get_single_evaluation_result(event_vector))

    def _calculate_affecting_vector(
        self,
        context: ExecutionContext,
        event_parsed_schema: EventParsedSchema,
        input_to_aggregate: OnlineNode,
    ) -> Vector:
        affecting_parsed_schema = self._map_event_schema_to_affecting_schema(
            event_parsed_schema
        )
        affecting_vector = input_to_aggregate.evaluate_next_single(
            affecting_parsed_schema, context
        ).main.value

        if not isinstance(affecting_vector, Vector):
            raise DagEvaluationException(
                "parent_to_aggregate's evaluation result must be of type Vector"
                + f", got {type(affecting_vector)}"
            )

        return affecting_vector

    def __check_schema_validity(self, schema: SchemaObject) -> None:
        if schema != self.node.affected_schema.schema:
            raise ValidationException(
                f"Unknown schema, {self.class_name} can only process"
                + f" {self.node.affected_schema.schema._base_class_name} "
                + f"got {schema._base_class_name}"
            )

    def _calculate_affecting_weights(
        self,
        event_parsed_schema: EventParsedSchema,
        context: ExecutionContext,
    ) -> Sequence[float]:
        return [
            weight
            for filter_parent, weight in self.weighted_filter_parents.items()
            if filter_parent.evaluate_next_single(
                event_parsed_schema, context
            ).main.value
        ]

    def _map_event_schema_to_affecting_schema(
        self, event_parsed_schema: EventParsedSchema
    ) -> ParsedSchema:
        return next(
            ParsedSchema(self.node.affecting_schema.schema, field.value, [])
            for field in event_parsed_schema.fields
            if field.schema_field == self.node.affecting_schema.reference_field
        )

    def _calculate_and_store_metadata(
        self,
        parsed_schema: ParsedSchemaWithEvent,
        new_effect_count: int,
    ) -> EventMetadata:
        stored_by_key = self._read_stored_metadata(parsed_schema)
        recalculated_effect_count = (
            stored_by_key.get(OnlineEventAggregationNode.EFFECT_COUNT_KEY) or 0
        ) + new_effect_count
        recalculated_avg_ts = self._calculate_avg_ts(
            stored_by_key, parsed_schema, recalculated_effect_count, new_effect_count
        )
        recalculated_oldest_ts = self._calculate_oldest_ts(stored_by_key, parsed_schema)
        self._write_updated_metadata(
            parsed_schema,
            recalculated_effect_count,
            recalculated_avg_ts,
            recalculated_oldest_ts,
        )
        return EventMetadata(
            recalculated_effect_count,
            recalculated_avg_ts,
            recalculated_oldest_ts,
        )

    def _read_stored_metadata(self, parsed_schema: ParsedSchemaWithEvent) -> dict:
        return self.storage_manager.read_node_data(
            parsed_schema.schema,
            parsed_schema.id_,
            self._metadata_key,
            {
                OnlineEventAggregationNode.EFFECT_COUNT_KEY: int,
                OnlineEventAggregationNode.EFFECT_AVG_TS_KEY: int,
                OnlineEventAggregationNode.EFFECT_OLDEST_TS_KEY: int,
            },
        )

    def _calculate_avg_ts(
        self,
        stored_by_key: dict,
        parsed_schema: ParsedSchemaWithEvent,
        recalculated_effect_count: int,
        new_effect_count: int,
    ) -> int:
        previous_avg_ts = stored_by_key.get(
            OnlineEventAggregationNode.EFFECT_AVG_TS_KEY
        )
        if previous_avg_ts and new_effect_count == 0:
            return previous_avg_ts
        return (
            math.ceil(  # ceil is used in case they are 1s apart
                (
                    previous_avg_ts * (recalculated_effect_count - new_effect_count)
                    + parsed_schema.event_parsed_schema.created_at
                )
                / recalculated_effect_count
            )
            if previous_avg_ts
            else parsed_schema.event_parsed_schema.created_at
        )

    def _calculate_oldest_ts(
        self, stored_by_key: dict, parsed_schema: ParsedSchemaWithEvent
    ) -> int:
        previous_oldest_ts = stored_by_key.get(
            OnlineEventAggregationNode.EFFECT_OLDEST_TS_KEY
        )
        return (
            min(previous_oldest_ts, parsed_schema.event_parsed_schema.created_at)
            if previous_oldest_ts
            else parsed_schema.event_parsed_schema.created_at
        )

    def _write_updated_metadata(
        self,
        parsed_schema: ParsedSchemaWithEvent,
        recalculated_effect_count: int,
        recalculated_avg_ts: int,
        recalculated_oldest_ts: int,
    ) -> None:
        self.storage_manager.write_node_data(
            parsed_schema.schema,
            parsed_schema.id_,
            self._metadata_key,
            {
                OnlineEventAggregationNode.EFFECT_COUNT_KEY: recalculated_effect_count,
                OnlineEventAggregationNode.EFFECT_AVG_TS_KEY: recalculated_avg_ts,
                OnlineEventAggregationNode.EFFECT_OLDEST_TS_KEY: recalculated_oldest_ts,
            },
        )
