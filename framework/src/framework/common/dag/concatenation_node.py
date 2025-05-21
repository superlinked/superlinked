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

import math

from beartype.typing import Any, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.persistence_params import PersistenceParams
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.space.config.normalization.normalization_config import (
    ConstantNormConfig,
)


class ConcatenationNode(Node[Vector], HasLength):
    def __init__(self, parents: list[Node[Vector]]) -> None:
        # Since events can change only a part of the whole result, we
        # must persist the rest of the parts.
        super().__init__(
            Vector,
            parents,
            persistence_params=PersistenceParams(persist_parent_node_result=True),
            non_nullable_parents=frozenset(parents),
        )
        self.__validate_parents()
        self.__length = sum(cast(HasLength, parent).length for parent in self.parents)

    def __validate_parents(self) -> None:
        if len(self.parents) == 0:
            raise ParentCountException(f"{self.class_name} must have at least 1 parent.")

    @property
    def length(self) -> int:
        return self.__length

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__}

    @override
    def project_parents_to_schema(self, schema: SchemaObject) -> Sequence[Node]:
        if schema in self.schemas:
            return self.parents
        return []

    def project_parents_for_dag_effect(self, dag_effect: DagEffect) -> Sequence[Node]:
        if dag_effect in self.dag_effects:
            return self.parents
        return []

    def create_normalization_config(self, weights: Sequence[float]) -> ConstantNormConfig:
        return ConstantNormConfig(math.sqrt(sum(weight**2 for weight in weights)) or 1.0)
