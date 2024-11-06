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

from beartype.typing import Mapping, Sequence
from PIL import Image
from PIL.ImageFile import ImageFile
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.image_information_node import ImageInformationNode
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.query.dag.query_evaluation_data_types import (
    QueryEvaluationResult,
)
from superlinked.framework.query.dag.query_node import QueryNode
from superlinked.framework.query.query_node_input import QueryNodeInput


class QueryImageInformationNode(QueryNode[ImageInformationNode, ImageData]):
    def __init__(
        self, node: ImageInformationNode, parents: Sequence[QueryNode]
    ) -> None:
        super().__init__(node, parents)
        self._blob_loader = BlobLoader(allow_bytes=True)

    @override
    def evaluate(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        context: ExecutionContext,
    ) -> QueryEvaluationResult[ImageData]:
        descriptions = self._get_field_values(inputs, self.node.description_node_id)
        opened_images = self.__open_images(inputs)
        weighted_image_data_from_images = [
            Weighted(
                ImageData(image=opened_image.item, description=None),
                opened_image.weight,
            )
            for opened_image in opened_images
        ]
        weighted_image_data_from_descriptions = [
            Weighted(
                ImageData(image=None, description=description.item), description.weight
            )
            for description in descriptions
        ]
        return QueryEvaluationResult(
            weighted_image_data_from_images + weighted_image_data_from_descriptions
        )

    def __open_images(
        self, inputs: Mapping[str, Sequence[QueryNodeInput]]
    ) -> list[Weighted[ImageFile]]:
        image_like_inputs = self._get_field_values(inputs, self.node.image_node_id)
        loaded_images = [
            self._blob_loader.load(image_like_input.item)
            for image_like_input in image_like_inputs
        ]
        opened_images = [
            Weighted(self._open_image(image.data), image_like_input.weight)
            for image, image_like_input in zip(loaded_images, image_like_inputs)
            if image.data is not None
        ]
        return opened_images

    def _open_image(self, image_data: bytes) -> ImageFile:
        return Image.open(io.BytesIO(base64.b64decode(image_data)))

    def _get_field_values(
        self,
        inputs: Mapping[str, Sequence[QueryNodeInput]],
        field_node_id: str,
    ) -> list[Weighted[str]]:
        field_values = [
            node_input.value
            for node_input in inputs.get(field_node_id, [])
            if node_input.value
            and node_input.value.item is not None
            and node_input.value.weight
        ]
        if wrong_field_values := [
            field_value
            for field_value in field_values
            if not isinstance(field_value.item, str)
        ]:
            raise ValueError(f"Invalid image parts: {wrong_field_values}.")
        return field_values
