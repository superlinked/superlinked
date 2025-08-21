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

from beartype.typing import Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InvalidInputException,
    InvalidStateException,
)
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
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
from superlinked.framework.online.online_entity_cache import OnlineEntityCache


class OnlineEventAggregationNode(OnlineNode[EventAggregationNode, Vector], HasLength):
    def __init__(
        self,
        node: EventAggregationNode,
        parents: list[OnlineNode],
    ) -> None:
        super().__init__(node, parents)
        self.__init_named_parents()
        self._transformation_config = self.node.transformation_config
        self._event_metadata_handler = EventMetadataHandler(self.node.node_id)
        self._event_effect_handler = EventEffectHandler()

    def __init_named_parents(self) -> None:
        inputs_to_aggregate = [
            parent for parent in self.parents if parent.node.node_id == self.node.input_to_aggregate.node_id
        ]
        if len(inputs_to_aggregate) > 1:
            raise InvalidStateException(
                f"{self.class_name} Cannot have more than 1 parents to aggregate.", len_parents=len(inputs_to_aggregate)
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
    async def evaluate_self(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[Vector] | None]:
        if not parsed_schemas:
            return []
        parsed_schema_types = list({type(parsed_schema) for parsed_schema in parsed_schemas})
        if len(parsed_schema_types) != 1:
            raise InvalidStateException("Cannot process a mix of event and non-event parsed schemas.")
        unique_object_ids = list({parsed_schema.id_ for parsed_schema in parsed_schemas})
        schema = self.__get_single_schema(parsed_schemas)
        id_to_result = await self._load_stored_result_by_id(schema, unique_object_ids, online_entity_cache)
        if self._input_to_aggregate is None or parsed_schema_types[0] != ParsedSchemaWithEvent:
            return self._to_evaluation_results(parsed_schemas, id_to_result)
        relevant_parsed_schemas = [
            parsed_schema
            for parsed_schema in cast(Sequence[ParsedSchemaWithEvent], parsed_schemas)
            if self.node.event_schema == parsed_schema.event_parsed_schema.schema
        ]

        event_id_to_affecting_info = await self._calculate_event_id_to_affecting_info(
            context, relevant_parsed_schemas, self._input_to_aggregate, online_entity_cache
        )
        for parsed_schema in relevant_parsed_schemas:
            if (event_id := parsed_schema.event_parsed_schema.id_) in event_id_to_affecting_info:
                affecting_info = event_id_to_affecting_info[event_id]
                stored_event_metadata = self._event_metadata_handler.read(
                    schema, parsed_schema.id_, online_entity_cache
                )
                recalculated_event_metadata = self._event_metadata_handler.recalculate(
                    parsed_schema.event_parsed_schema.created_at,
                    affecting_info.number_of_weights,
                    stored_event_metadata,
                )
                id_to_result[parsed_schema.id_] = await EventAggregator(
                    EventAggregatorParams(
                        context,
                        id_to_result[parsed_schema.id_],
                        Weighted(affecting_info.affecting_vector, affecting_info.average_weight),
                        recalculated_event_metadata,
                        self.node.effect_modifier,
                        self._transformation_config,
                    )
                ).calculate_event_vector()
                self._event_metadata_handler.write(
                    schema, {parsed_schema.id_: recalculated_event_metadata}, online_entity_cache
                )

        return self._to_evaluation_results(parsed_schemas, id_to_result)

    def _to_evaluation_results(
        self, parsed_schemas: Sequence[ParsedSchema], id_to_result: Mapping[str, Vector]
    ) -> list[EvaluationResult[Vector] | None]:
        return [self.__to_evaluation_result(id_to_result[parsed_schema.id_]) for parsed_schema in parsed_schemas]

    def __to_evaluation_result(self, result: Vector) -> EvaluationResult[Vector] | None:
        # Return None for empty vectors to prevent storing empty vectors in the database
        if result.is_empty:
            return None
        return EvaluationResult(self._get_single_evaluation_result(result))

    def __get_single_schema(self, parsed_schemas: Sequence[ParsedSchema]) -> IdSchemaObject:
        for parsed_schema in parsed_schemas:
            if parsed_schema.schema != self.node.affected_schema.schema:
                raise InvalidInputException(
                    f"Unknown schema, {self.class_name} can only process"
                    + f" {self.node.affected_schema.schema._base_class_name} "
                    + f"got {parsed_schema.schema._base_class_name}"
                )
        return parsed_schemas[0].schema

    async def _load_stored_result_by_id(
        self,
        schema: IdSchemaObject,
        object_ids: Sequence[str],
        online_entity_cache: OnlineEntityCache,
    ) -> dict[str, Vector]:
        stored_results = await self.load_stored_results(
            [(schema, object_id) for object_id in object_ids], online_entity_cache
        )
        return {
            object_id: stored_result or Vector.empty_vector()
            for object_id, stored_result in zip(object_ids, stored_results)
        }

    async def _calculate_event_id_to_affecting_info(
        self,
        context: ExecutionContext,
        parsed_schemas: Sequence[ParsedSchemaWithEvent],
        input_to_aggregate: OnlineNode,
        online_entity_cache: OnlineEntityCache,
    ) -> dict[str, EventAffectingInfo]:
        event_parsed_schemas = [parsed_schema.event_parsed_schema for parsed_schema in parsed_schemas]
        vectors = await self._calculate_affecting_vectors(
            context, event_parsed_schemas, input_to_aggregate, online_entity_cache
        )
        weights = await self._calculate_affecting_weights(context, event_parsed_schemas, online_entity_cache)
        return self._event_effect_handler.calculate_affecting_info_by_event_id(event_parsed_schemas, vectors, weights)

    async def _calculate_affecting_vectors(
        self,
        context: ExecutionContext,
        event_parsed_schemas: Sequence[EventParsedSchema],
        input_to_aggregate: OnlineNode,
        online_entity_cache: OnlineEntityCache,
    ) -> list[Vector]:
        affecting_parsed_schemas = [
            self._event_effect_handler.map_event_schema_to_affecting_schema(
                self.node.affecting_schema, event_parsed_schema
            )
            for event_parsed_schema in event_parsed_schemas
        ]
        parent_results = await self.evaluate_parent(
            input_to_aggregate, affecting_parsed_schemas, context, online_entity_cache
        )
        return [
            self._event_effect_handler.map_parent_result_to_vector(parent_result) for parent_result in parent_results
        ]

    async def _calculate_affecting_weights(
        self,
        context: ExecutionContext,
        event_parsed_schemas: Sequence[EventParsedSchema],
        online_entity_cache: OnlineEntityCache,
    ) -> list[list[float]]:
        filter_parents = list(self.weighted_filter_parents.keys())
        parent_results = await self.evaluate_parents(filter_parents, event_parsed_schemas, context, online_entity_cache)
        affecting_weights = [
            [self.weighted_filter_parents[parent] for parent, result in parent_result.items() if result.main.value]
            for parent_result in parent_results
        ]
        return affecting_weights
