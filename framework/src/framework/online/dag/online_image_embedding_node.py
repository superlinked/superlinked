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

import base64
import io

from beartype.typing import Sequence, cast
from PIL import Image
from PIL.ImageFile import ImageFile
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import PythonTypes, Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.transform.transform import Step
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode


class OnlineImageEmbeddingNode(OnlineNode[ImageEmbeddingNode, Vector], HasLength):
    def __init__(
        self,
        node: ImageEmbeddingNode,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__(node, parents, storage_manager)
        self._embedding_transformation = self._init_embedding_transformation()
        self._blob_loader = BlobLoader(allow_bytes=True)
        self._description_node = self._get_schema_field_node(
            self.node.description_node_id
        )
        self._image_node = self._get_schema_field_node(self.node.image_node_id)

    def _get_schema_field_node(self, node_id: str | None) -> SchemaFieldNode | None:
        if node_id is None:
            return None
        return next(
            (
                cast(SchemaFieldNode, parent.node)
                for parent in self.parents
                if parent.node_id == node_id
            ),
            None,
        )

    def _init_embedding_transformation(self) -> Step[Sequence[ImageData], list[Vector]]:
        return TransformationFactory.create_multi_embedding_transformation(
            self.node.transformation_config
        )

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @property
    def embedding_transformation(self) -> Step[Sequence[ImageData], list[Vector]]:
        return self._embedding_transformation

    @override
    def evaluate_self(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[Vector]]:
        if context.should_load_default_node_input:
            result = EvaluationResult(
                self._get_single_evaluation_result(
                    self.node.transformation_config.embedding_config.default_vector
                )
            )
            return [result] * len(parsed_schemas)
        image_data_list = [
            self._get_image_data(parsed_schema) for parsed_schema in parsed_schemas
        ]
        embedded_images = self.embedding_transformation.transform(
            image_data_list, context
        )

        return [
            EvaluationResult(self._get_single_evaluation_result(embedded_image))
            for embedded_image in embedded_images
        ]

    def _get_image_data(self, parsed_schema: ParsedSchema) -> ImageData:
        image, description = self.__load_input(parsed_schema)
        loaded_image: ImageFile | None = None
        if image is not None and image.data is not None:
            loaded_image = Image.open(io.BytesIO(base64.b64decode(image.data)))
        return ImageData(loaded_image, description)

    def __load_input(
        self, parsed_schema: ParsedSchema
    ) -> tuple[BlobInformation | None, str | None]:
        description = self._get_field_value(parsed_schema, self._description_node)
        if description is not None and not isinstance(description, str):
            raise ValueError(
                f"Invalid image description type: {type(description).__name__}."
            )
        image = self._get_field_value(parsed_schema, self._image_node)
        if image is not None and not isinstance(image, BlobInformation):
            image = self._blob_loader.load(image)
        return image, (description if description else None)

    def _get_field_value(
        self,
        parsed_schema: ParsedSchema,
        schema_field_node: SchemaFieldNode | None,
    ) -> PythonTypes | None:
        if schema_field_node is None:
            return None
        return next(
            (
                field.value
                for field in parsed_schema.fields
                if field.schema_field == schema_field_node.schema_field
            ),
            None,
        )
