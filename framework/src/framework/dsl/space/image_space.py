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

from pathlib import Path

import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.image_embedding_node import ImageEmbeddingNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.schema.schema_object import (
    Blob,
    DescribedBlob,
    SchemaObject,
    String,
)
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    VectorAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.image_embedding_config import (
    ImageEmbeddingConfig,
    ModelHandler,
)
from superlinked.framework.common.space.config.normalization.normalization_config import (
    L2NormConfig,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.space.embedding.image_embedding import ImageEmbedding
from superlinked.framework.dsl.space.exception import InvalidSpaceParamException
from superlinked.framework.dsl.space.image_space_field_set import (
    ImageDescriptionSpaceFieldSet,
    ImageSpaceFieldSet,
)
from superlinked.framework.dsl.space.space import Space

logger = structlog.getLogger()

DEFAULT_DESCRIPTION_FIELD_PREFIX = "__SL_DEFAULT_DESCRIPTION_"


class ImageSpace(Space[Vector, ImageData]):
    """
    Initialize the ImageSpace instance for generating vector representations
    from images, supporting models from the OpenCLIP project.

    Args:
        image (Blob | DescribedBlob | Sequence[Blob | DescribedBlob]):
            The image content as a Blob or DescribedBlob (write image+description), or a sequence of them.
        model (str, optional): The model identifier for generating image embeddings.
            Defaults to "clip-ViT-B-32".
        model_handler (ModelHandler, optional): The handler for the model,
            defaults to ModelHandler.SENTENCE_TRANSFORMERS.

    Raises:
        InvalidSpaceParamException: If the image and description fields are not
            from the same schema.
    """

    def __init__(
        self,
        image: Blob | DescribedBlob | Sequence[Blob | DescribedBlob],
        model: str = "clip-ViT-B-32",
        model_handler: ModelHandler = ModelHandler.SENTENCE_TRANSFORMERS,
        model_cache_dir: Path | None = None,
    ) -> None:
        """
        Initialize the ImageSpace instance for generating vector representations
        from images, supporting models from the OpenCLIP project.

        Args:
            image (Blob | DescribedBlob | Sequence[Blob | DescribedBlob]):
                The image content as a Blob or DescribedBlob (write image+description), or a sequence of them.
            model (str, optional): The model identifier for generating image embeddings.
                Defaults to "clip-ViT-B-32".
            model_handler (ModelHandler, optional): The handler for the model,
                defaults to ModelHandler.SENTENCE_TRANSFORMERS.
            model_cache_dir (Path | None, optional): Directory to cache downloaded models.
                If None, uses the default cache directory. Defaults to None.

        Raises:
            InvalidSpaceParamException: If the image and description fields are not
                from the same schema.
        """
        described_blobs = [self._get_described_blob(img) for img in (image if isinstance(image, Sequence) else [image])]
        image_fields = [described.blob for described in described_blobs]
        super().__init__(image_fields, Blob)
        length = ImageEmbedding.init_manager(model_handler, model, model_cache_dir).calculate_length()
        self.image = ImageSpaceFieldSet(self, set(image_fields))
        self.description = ImageDescriptionSpaceFieldSet(
            self, set(described.description for described in described_blobs)
        )
        self._all_fields = self.image.fields | self.description.fields
        self._transformation_config = self._init_transformation_config(model, length, model_handler)
        self._schema_field_nodes_by_schema: dict[
            SchemaObject, tuple[SchemaFieldNode[BlobInformation], SchemaFieldNode[str]]
        ] = {
            described_blob.blob.schema_obj: (
                SchemaFieldNode(described_blob.blob),
                SchemaFieldNode(described_blob.description),
            )
            for described_blob in described_blobs
        }
        self.__embedding_node_by_schema: dict[SchemaObject, EmbeddingNode[Vector, ImageData]] = {
            schema: ImageEmbeddingNode(
                image_blob_node=image_blob_node,
                description_node=description_node,
                transformation_config=self.transformation_config,
                fields_for_identification=self._all_fields,
            )
            for schema, (
                image_blob_node,
                description_node,
            ) in self._schema_field_nodes_by_schema.items()
        }
        self._model = model

    def _get_described_blob(self, image: Blob | DescribedBlob) -> DescribedBlob:
        if isinstance(image, DescribedBlob):
            if image.description.schema_obj != image.blob.schema_obj:
                raise InvalidSpaceParamException("ImageSpace image and description field must be in the same schema.")
            return image
        description = String(DEFAULT_DESCRIPTION_FIELD_PREFIX + image.name, image.schema_obj)
        return DescribedBlob(image, description)

    @property
    @override
    def transformation_config(self) -> TransformationConfig[Vector, ImageData]:
        return self._transformation_config

    @property
    @override
    def _embedding_node_by_schema(
        self,
    ) -> dict[SchemaObject, EmbeddingNode[Vector, ImageData]]:
        return self.__embedding_node_by_schema

    @override
    def _create_default_node(self, schema: SchemaObject) -> EmbeddingNode[Vector, ImageData]:
        default_node = ImageEmbeddingNode(None, None, self._transformation_config, self._all_fields, schema)
        return default_node

    @property
    @override
    def _annotation(self) -> str:
        return f"""The space encodes images using {self._model} embeddings.
        Affected fields: {self.description.field_names_text}.
        Negative weight would mean favoring images with descriptions that are semantically dissimilar
        to the one present in the .similar clause corresponding to this space.
        Zero weight means insensitivity, positive weights mean favoring images with similar descriptions.
        Larger positive weights increase the effect on similarity compared to other spaces.
        Accepts str type input describing an image for a corresponding .similar clause input."""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return False

    def _init_transformation_config(
        self, model: str, length: int, model_handler: ModelHandler
    ) -> TransformationConfig[Vector, ImageData]:
        embedding_config = ImageEmbeddingConfig(
            ImageData,
            model,
            model_handler,
            length,
        )
        aggregation_config = VectorAggregationConfig(Vector)
        normalization_config = L2NormConfig()
        return TransformationConfig(normalization_config, aggregation_config, embedding_config)
