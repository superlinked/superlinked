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

from beartype.typing import Any, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.comparison_filter_node import ComparisonFilterNode
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.persistence_params import PersistenceParams
from superlinked.framework.common.dag.schema_object_reference import (
    SchemaObjectReference,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.dsl.index.effect import EffectModifier


class EventAggregationNode(
    Node[Vector], HasLength
):  # pylint: disable=too-many-instance-attributes
    @dataclass
    class InitParams:
        input_to_aggregate: Node[Vector]
        event_schema: EventSchemaObject
        affected_schema: SchemaObjectReference
        affecting_schema: SchemaObjectReference
        filter_inputs: list[Weighted[ComparisonFilterNode]]
        dag_effects: set[DagEffect]
        effect_modifier: EffectModifier

    def __init__(self, init_params: InitParams) -> None:
        super().__init__(
            Vector,
            [init_params.input_to_aggregate]
            + [filter.item for filter in init_params.filter_inputs],
            dag_effects=set(init_params.dag_effects),
            persistence_params=PersistenceParams(
                persist_evaluation_result=True, persist_parent_evaluation_result=True
            ),
        )
        self.schemas = {
            init_params.event_schema,
            init_params.affected_schema.schema,
        }
        self.input_to_aggregate = init_params.input_to_aggregate
        self.event_schema = init_params.event_schema
        self.affected_schema = init_params.affected_schema
        self.affecting_schema = init_params.affecting_schema
        self.filters = init_params.filter_inputs
        self.effect_modifier = init_params.effect_modifier
        self.__length = cast(HasLength, self.parents[0]).length

    @property
    def length(self) -> int:
        return self.__length

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        filters = [
            {"node_id": filter_.item.node_id, "weight": filter_.weight}
            for filter_ in self.filters
        ]
        return {
            "dag_effects": self.dag_effects,
            "schemas": self.schemas,
            "event_schema": self.event_schema,
            "affected_schema": self.affected_schema,
            "affecting_schema": self.affecting_schema,
            "filters": filters,
        }

    @override
    def project_parents_to_schema(self, schema: SchemaObject) -> Sequence[Node]:
        if schema == self.event_schema:
            return self.parents
        return []

    def project_parents_for_dag_effect(self, dag_effect: DagEffect) -> Sequence[Node]:
        if dag_effect in self.dag_effects:
            return self.parents
        return []
