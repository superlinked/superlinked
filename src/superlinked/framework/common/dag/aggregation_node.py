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

from typing import cast

from typing_extensions import override

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.persistence_params import PersistenceParams
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import ValidationException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.schema.schema_object import SchemaObject


class AggregationNode(Node[Vector], HasLength):
    def __init__(
        self,
        weighted_parents: list[Weighted[Node[Vector]]],
        dag_effects: set[DagEffect],
    ) -> None:
        super().__init__(
            [weighted_parent.item for weighted_parent in weighted_parents],
            persistence_params=PersistenceParams(persist_parent_evaluation_result=True),
        )
        self.dag_effects = dag_effects
        self.__validate_parents()
        self.weighted_parents = weighted_parents
        # All parents are of the same length as it was validated earlier.
        self.__length = cast(HasLength, self.parents[0]).length

    def __validate_parents(self) -> None:
        if len(self.parents) == 0:
            raise ParentCountException(
                f"{self.class_name} must have at least 1 parent."
            )
        length = cast(HasLength, self.parents[0]).length
        wrong_length_parents = {
            parent
            for parent in self.parents
            if cast(HasLength, parent).length != length
        }
        if any(wrong_length_parents):
            lengths = {length}.union(
                {cast(HasLength, parent).length for parent in wrong_length_parents}
            )
            raise ValidationException(
                f"{self.class_name} must have parents with the same length, got {lengths}"
            )

    @property
    def length(self) -> int:
        return self.__length

    @override
    @property
    def persist_evaluation_result(self) -> bool:
        # Aggregation node's parents are always persisted, no need for double persistence.
        return False

    @override
    def project_parents_to_schema(self, schema: SchemaObject) -> list[Node]:
        if schema in self.schemas:
            return self.parents
        return []

    def project_parents_for_dag_effect(self, dag_effect: DagEffect) -> list[Node]:
        if dag_effect in self.dag_effects:
            return self.parents
        return []
