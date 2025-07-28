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

from beartype.typing import Any, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.schema.schema_object import SchemaField


class ComparisonFilterNode(Node[bool]):
    def __init__(
        self,
        parent: SchemaFieldNode,
        comparison_operation: ComparisonOperation[SchemaField],
        dag_effects: set[DagEffect] | None = None,
    ) -> None:
        if parent.schema_field != comparison_operation._operand:
            raise InvalidStateException(f"{self.class_name}'s parent and operand must be the same.")
        super().__init__(bool, [parent], non_nullable_parents=frozenset([parent]))
        if dag_effects is not None:
            self.dag_effects = dag_effects
        self.comparison_operation = comparison_operation

    @property
    @override
    def persist_node_result(self) -> bool:
        # ComparisonFilterNode's result is bool, currently it cannot be persisted.
        return False

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        schema_field = cast(SchemaField, self.comparison_operation._operand)
        return {
            "comparison_operation": {
                "schema": schema_field.schema_obj._schema_name,
                "schema_field": schema_field.name,
                "op": self.comparison_operation._op.value,
                "other": self.comparison_operation._other,
            },
            "dag_effects": self.dag_effects,
        }

    @override
    def project_parents_for_dag_effect(self, dag_effect: DagEffect) -> Sequence[Node]:
        return self.parents
