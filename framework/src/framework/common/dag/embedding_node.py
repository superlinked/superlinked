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


import hashlib

from beartype.typing import Any, Generic, Sequence, TypeVar
from typing_extensions import override

from superlinked.framework.common.dag.node import Node, NodeDataT
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.space.interface.has_transformation_config import (
    HasTransformationConfig,
)


class EmbeddingNode(
    Generic[AggregationInputT, NodeDataT],
    Node[Vector],
    HasTransformationConfig[AggregationInputT, NodeDataT],
):
    def __init__(
        self,
        parents: Sequence[Node | None],
        transformation_config: TransformationConfig[AggregationInputT, NodeDataT],
        fields_for_identification: set[SchemaField],
        schema: IdSchemaObject | None = None,
    ) -> None:
        super().__init__(
            Vector,
            [parent for parent in parents if parent is not None],
            {schema} if schema else None,
        )
        self._identifier = self._calculate_node_id_identifier(fields_for_identification)
        self._transformation_config = transformation_config

    @property
    @override
    def length(self) -> int:
        return self._transformation_config.length

    @property
    @override
    def transformation_config(
        self,
    ) -> TransformationConfig[AggregationInputT, NodeDataT]:
        return self._transformation_config

    def _calculate_node_id_identifier(self, fields: set[SchemaField]) -> str:
        """
        This method ensures unique node ID generation by creating a hash of
        - concatenated field names when multiple fields exist
        - concatenated schema names when multiple schemas exist
        This prevents ID collisions between different spaces that may
        share some of the same fields and have the same configuration.
        """
        if len(fields) == 0 and len(self.schemas) == 0:
            return ""
        field_names_text = str(sorted([field.name for field in fields]))
        schema_names_text = str(sorted([schema._schema_name for schema in self.schemas]))
        return hashlib.md5((field_names_text + schema_names_text).encode()).hexdigest()[:8]

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {
            "transformation_config": self.transformation_config._get_embedding_config_parameters(),
            "identifier": self._identifier,
        }


EmbeddingNodeT = TypeVar("EmbeddingNodeT", bound=EmbeddingNode)
