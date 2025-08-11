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
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)


class ImageEmbeddingNode(EmbeddingNode[Vector, ImageData]):
    def __init__(
        self,
        image_blob_node: Node[BlobInformation] | None,
        description_node: Node[str] | None,
        transformation_config: TransformationConfig[Vector, ImageData],
        fields_for_identification: set[SchemaField],
        schema: IdSchemaObject | None = None,
    ) -> None:
        super().__init__(
            [image_blob_node, description_node],
            transformation_config,
            fields_for_identification,
            schema,
        )
        self.image_node_id = image_blob_node.node_id if image_blob_node else None
        self.description_node_id = description_node.node_id if description_node else None
