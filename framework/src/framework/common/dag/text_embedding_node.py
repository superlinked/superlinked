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

from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)


class TextEmbeddingNode(EmbeddingNode[Vector, str]):
    def __init__(
        self,
        parent: Node[str] | None,
        transformation_config: TransformationConfig[Vector, str],
        fields_for_identification: set[SchemaField],
        schema: IdSchemaObject | None = None,
        salt: str | None = None,
    ) -> None:
        super().__init__([parent], transformation_config, fields_for_identification, schema, salt)
