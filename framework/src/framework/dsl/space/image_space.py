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

import structlog
from beartype.typing import Sequence, cast
from typing_extensions import override

from superlinked.framework.common.dag.constant_node import ConstantNode
from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.dag.image_information_node import ImageInformationNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.schema.schema_object import (
    Blob,
    DescribedBlob,
    SchemaField,
    SchemaObject,
    String,
)
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    VectorAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.image_embedding_config import (
    ImageEmbeddingConfig,
)
from superlinked.framework.common.space.config.normalization.normalization_config import (
    L2NormConfig,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.space.embedding.sentence_transformer_manager import (
    SentenceTransformerManager,
)
from superlinked.framework.dsl.space.exception import InvalidSpaceParamException
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

logger = structlog.getLogger()

DEFAULT_DESCRIPTION_FIELD_PREFIX = "__SL_DEFAULT_DESCRIPTION_"


class ImageSpace(Space[Vector, ImageData]):
    """
    Initialize the ImageSpace instance.

    This constructor sets up an ImageSpace, which is used to generate
    vector representations from images for search and retrieval tasks.
    It supports models from the (OpenCLIP)[https://github.com/mlfoundations/open_clip] project.

    Args:
        image (Blob): The image content encapsulated as a Blob object.
            This represents the raw image data to be processed.
        description (String, optional): A description of the image content.
            This should be a SchemaFieldObject of type String, not a standard
            Python string. It provides additional context for the image.
            If not provided, a default description field is used.
        model (str, optional): The identifier for the model used to generate
            image embeddings. Defaults to "clip-ViT-B-32". This model
            determines the method of embedding the image into a vector space.

    Raises:
        InvalidSpaceParamException: If the image and description fields
            do not belong to the same schema.
    """

    def __init__(
        self,
        image: Blob | DescribedBlob | Sequence[Blob | DescribedBlob],
        model: str = "clip-ViT-B-32",
    ) -> None:
        """
        Initialize the ImageSpace instance.

        This constructor sets up an ImageSpace, which is used to generate
        vector representations from images for search and retrieval tasks.
        It supports models from the (OpenCLIP)[https://github.com/mlfoundations/open_clip] project.

        Args:
            image (Blob): The image content encapsulated as a Blob object.
                This represents the raw image data to be processed.
            description (String, optional): A description of the image content.
                This should be a SchemaFieldObject of type String, not a standard
                Python string. It provides additional context for the image.
                If not provided, a default description field is used.
            model (str, optional): The identifier for the model used to generate
                image embeddings. Defaults to "clip-ViT-B-32". This model
                determines the method of embedding the image into a vector space.

        Raises:
            InvalidSpaceParamException: If the image and description fields
                do not belong to the same schema.
        """
        length = SentenceTransformerManager.calculate_length(model)
        self._transformation_config = self._init_transformation_config(model, length)
        described_blobs = [
            self._get_described_blob(img)
            for img in (image if isinstance(image, Sequence) else [image])
        ]
        image_fields = [described.blob for described in described_blobs]
        super().__init__(image_fields, Blob)
        self.image = SpaceFieldSet(self, set(image_fields))
        self.description = SpaceFieldSet(
            self, set(described.description for described in described_blobs)
        )

        self._schema_field_nodes_by_schema: dict[
            SchemaObject, tuple[SchemaFieldNode[BlobInformation], SchemaFieldNode[str]]
        ] = {
            described_blob.blob.schema_obj: (
                SchemaFieldNode(described_blob.blob),
                SchemaFieldNode(described_blob.description),
            )
            for described_blob in described_blobs
        }
        self._schema_node_map: dict[SchemaObject, EmbeddingNode[Vector, ImageData]] = {
            schema: ImageEmbeddingNode(
                parent=ImageInformationNode(image_blob_node, description_node),
                transformation_config=self.transformation_config,
            )
            for schema, (
                image_blob_node,
                description_node,
            ) in self._schema_field_nodes_by_schema.items()
        }
        self._model = model
        logger.warning(
            "Image space is experimental and isn't ready for production use."
        )

    def _get_described_blob(self, image: Blob | DescribedBlob) -> DescribedBlob:
        if isinstance(image, DescribedBlob):
            if image.description.schema_obj != image.blob.schema_obj:
                raise InvalidSpaceParamException(
                    "ImageSpace image and description field must be in the same schema."
                )
            return image
        description = String(
            DEFAULT_DESCRIPTION_FIELD_PREFIX + image.name, image.schema_obj
        )
        return DescribedBlob(image, description)

    def get_node_id(self, schema_field: SchemaField) -> str:
        image_node, description_node = self._schema_field_nodes_by_schema[
            schema_field.schema_obj
        ]
        if schema_field == image_node.schema_field:
            return image_node.node_id
        if schema_field == description_node.schema_field:
            return description_node.node_id
        raise QueryException("Invalid field for the given schema.")

    @property
    @override
    def transformation_config(self) -> TransformationConfig[Vector, ImageData]:
        return self._transformation_config

    @property
    @override
    def _node_by_schema(self) -> dict[SchemaObject, EmbeddingNode[Vector, ImageData]]:
        return self._schema_node_map

    @override
    def _create_default_node(
        self, schema: SchemaObject
    ) -> EmbeddingNode[Vector, ImageData]:
        default_value = ImageData(None, None)
        constant_node = cast(Node, ConstantNode(value=default_value, schema=schema))
        default_node = ImageEmbeddingNode(constant_node, self._transformation_config)
        return default_node

    @property
    @override
    def annotation(self) -> str:
        return f"""The space encodes images using {self._model} embeddings.
        Negative weight would mean favoring images with descriptions that are semantically dissimilar
        to the one present in the .similar clause corresponding to this space.
        Zero weight means insensitivity, positive weights mean favoring images with similar descriptions.
        Larger positive weights increase the effect on similarity compared to other spaces.
        Space weights do not matter if there is only 1 space in the query.
        Accepts str type input describing an image for a corresponding .similar clause input."""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return False

    def _init_transformation_config(
        self, model: str, length: int
    ) -> TransformationConfig[Vector, ImageData]:
        embedding_config = ImageEmbeddingConfig(ImageData, model, length)
        aggregation_config = VectorAggregationConfig(Vector)
        normalization_config = L2NormConfig()
        return TransformationConfig(
            normalization_config, aggregation_config, embedding_config
        )
