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

import asyncio
from itertools import chain

from beartype.typing import Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import PythonTypes, Vector
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.transform.transform import Step
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.common.util.image_util import PILImage
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.online_entity_cache import OnlineEntityCache


class OnlineImageEmbeddingNode(OnlineNode[ImageEmbeddingNode, Vector], HasLength):
    def __init__(
        self,
        node: ImageEmbeddingNode,
        parents: list[OnlineNode],
    ) -> None:
        super().__init__(node, parents)
        self._embedding_transformation = self._init_embedding_transformation()
        self._blob_loader = BlobLoader(allow_bytes=True)
        self._description_node = self._get_schema_field_node(self.node.description_node_id)
        self._image_node = self._get_schema_field_node(self.node.image_node_id)

    def _get_schema_field_node(self, node_id: str | None) -> SchemaFieldNode | None:
        if node_id is None:
            return None
        return next(
            (cast(SchemaFieldNode, parent.node) for parent in self.parents if parent.node_id == node_id),
            None,
        )

    def _init_embedding_transformation(self) -> Step[Sequence[ImageData], list[Vector]]:
        return TransformationFactory.create_multi_embedding_transformation(self.node.transformation_config)

    @property
    @override
    def length(self) -> int:
        return self.node.length

    @property
    def embedding_transformation(self) -> Step[Sequence[ImageData], list[Vector]]:
        return self._embedding_transformation

    @override
    async def evaluate_self(  # pylint: disable=too-many-locals
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[Vector] | None]:
        image_data_list = await asyncio.gather(
            *[self._get_image_data(parsed_schema) for parsed_schema in parsed_schemas]
        )
        empty_indices = []
        valid_indices = []
        valid_image_data = []
        empty_parsed_schemas = []
        for i, image_data in enumerate(image_data_list):
            if image_data.image is None and image_data.description is None:
                empty_indices.append(i)
                empty_parsed_schemas.append(parsed_schemas[i])
            else:
                valid_indices.append(i)
                valid_image_data.append(image_data_list[i])
        empty_results = await self.load_stored_results_with_default(
            [(parsed_schema.schema, parsed_schema.id_) for parsed_schema in empty_parsed_schemas],
            self.node.transformation_config.embedding_config.default_vector,
            online_entity_cache,
        )
        valid_results = await self.embedding_transformation.transform(valid_image_data, context)
        results: list[EvaluationResult[Vector] | None] = [None] * len(image_data_list)  # type: ignore
        for idx, result in chain(zip(empty_indices, empty_results), zip(valid_indices, valid_results)):
            results[idx] = EvaluationResult(self._get_single_evaluation_result(result))
        return results

    async def _get_image_data(self, parsed_schema: ParsedSchema) -> ImageData:
        image, description = await self.__load_input(parsed_schema)
        loaded_image: PILImage | None = image.data if image and image.data else None
        return ImageData(loaded_image, description)

    async def __load_input(self, parsed_schema: ParsedSchema) -> tuple[BlobInformation | None, str | None]:
        description = self._get_field_value(parsed_schema, self._description_node)
        if description is not None and not isinstance(description, str):
            raise InvalidStateException("Invalid image description type.", description_type=type(description).__name__)
        image = self._get_field_value(parsed_schema, self._image_node)
        if image is not None and not isinstance(image, BlobInformation):
            image = (await self._blob_loader.load([image]))[0]
        return image, (description if description else None)

    def _get_field_value(
        self,
        parsed_schema: ParsedSchema,
        schema_field_node: SchemaFieldNode | None,
    ) -> PythonTypes | None:
        if schema_field_node is None:
            return None
        return next(
            (field.value for field in parsed_schema.fields if field.schema_field == schema_field_node.schema_field),
            None,
        )
