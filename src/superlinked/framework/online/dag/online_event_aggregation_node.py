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

from typing_extensions import override

from superlinked.framework.common.const import DEFAULT_WEIGHT
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    DagEvaluationException,
    ValidationException,
)
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.exception import ParentCountException
from superlinked.framework.online.dag.online_comparison_filter_node import (
    OnlineComparisonFilterNode,
)
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineEventAggregationNode(OnlineNode[EventAggregationNode, Vector], HasLength):
    EFFECT_COUNT_KEY = "effect_count"

    @dataclass
    class EventEffect:
        aggregation: Vector
        effect_count: int

    def __init__(
        self,
        node: EventAggregationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, parents, evaluation_result_store_manager)
        self.__init_named_parents()

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
        self.input_to_aggregate = (
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
            DEFAULT_WEIGHT,
        )

    @classmethod
    def from_node(
        cls,
        node: EventAggregationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineEventAggregationNode:
        return cls(node, parents, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[EventAggregationNode]:
        return EventAggregationNode

    @property
    def length(self) -> int:
        return self.node.length

    @override
    def evaluate_self(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[Vector]:
        self.__check_schema_validity(parsed_schema.schema)
        stored_result = (
            self.load_stored_result(parsed_schema.id_, parsed_schema.schema)
            or Vector.empty_vector()
        )
        if (
            parsed_schema.event_parsed_schema is None
            or self.node.event_schema != parsed_schema.event_parsed_schema.schema
            or self.input_to_aggregate is None
        ):
            return EvaluationResult(self._get_single_evaluation_result(stored_result))
        previous_result = stored_result
        event_effect = self._process_event(parsed_schema.event_parsed_schema, context)

        previous_effect_count = self.__load_effect_count(
            parsed_schema.id_, parsed_schema.schema
        )
        accumulated_previous_result = (
            Vector.empty_vector()
            if previous_effect_count == 0
            else (previous_result * previous_effect_count)
        )
        new_effect_count = previous_effect_count + event_effect.effect_count
        vector = (
            (accumulated_previous_result.aggregate(event_effect.aggregation))
            / new_effect_count
            if new_effect_count
            else Vector.empty_vector()
        )
        self.__store_effect_count(
            parsed_schema.id_, parsed_schema.schema, new_effect_count
        )
        result = self._get_single_evaluation_result(vector)
        return EvaluationResult(result)

    def __check_schema_validity(self, schema: SchemaObject) -> None:
        if schema != self.node.affected_schema.schema:
            raise ValidationException(
                f"Unknown schema, {self.class_name} can only process"
                + f" {self.node.affected_schema.schema._base_class_name} "
                + f"got {schema._base_class_name}"
            )

    def _process_event(
        self,
        event_parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EventEffect:
        if self.input_to_aggregate is None:
            raise DagEvaluationException(
                f"{self.class_name} must have an input to aggregate."
            )

        affecting_parsed_schema = self._map_event_schema_to_affecting_schema(
            event_parsed_schema
        )
        parent_result = self.input_to_aggregate.evaluate_next(
            affecting_parsed_schema, context
        ).main.value
        if not isinstance(parent_result, Vector):
            raise DagEvaluationException(
                "parent_to_aggregate's evaluation result must be of type Vector"
                + f", got {type(parent_result)}"
            )
        event_effect = self._aggregate_event_effect(
            event_parsed_schema, parent_result, context
        )
        return event_effect

    def _aggregate_event_effect(
        self,
        event_parsed_schema: ParsedSchema,
        affecting_vector: Vector,
        context: ExecutionContext,
    ) -> EventEffect:
        aggregated_vector: Vector = Vector.empty_vector()
        effect_count = 0
        if not affecting_vector.is_empty:
            for filter_parent, weight in self.weighted_filter_parents.items():
                filter_result = filter_parent.evaluate_next(
                    event_parsed_schema,
                    context,
                )
                if filter_result.main.value:
                    weighted_affecting_vector = affecting_vector * weight
                    aggregated_vector = aggregated_vector.aggregate(
                        weighted_affecting_vector
                    )
                    effect_count += 1
        return OnlineEventAggregationNode.EventEffect(aggregated_vector, effect_count)

    def _map_event_schema_to_affecting_schema(
        self, event_parsed_schema: ParsedSchema
    ) -> ParsedSchema:
        return next(
            ParsedSchema(self.node.affecting_schema.schema, field.value, [])
            for field in event_parsed_schema.fields
            if field.schema_field == self.node.affecting_schema.reference_field
        )

    def __store_effect_count(
        self, main_object_id: str, schema: SchemaObject, count: int
    ) -> None:
        self.evaluation_result_store_manager.save_result_meta(
            EvaluationResultStoreManager.SaveResultMetaArgs(
                main_object_id,
                schema._schema_name,
                self.node_id,
                OnlineEventAggregationNode.EFFECT_COUNT_KEY,
                str(count),
            )
        )

    def __load_effect_count(
        self,
        main_object_id: str,
        schema: SchemaObject,
    ) -> int:
        count = int(
            self.evaluation_result_store_manager.load_result_meta(
                main_object_id,
                schema._schema_name,
                self.node_id,
                OnlineEventAggregationNode.EFFECT_COUNT_KEY,
            )
            or 0
        )
        return count
