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
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.image_data import ImageData
from superlinked.framework.common.schema.schema_object import (
    Blob,
    DescribedBlob,
    SchemaField,
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
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)
from superlinked.framework.common.space.embedding.model_based.engine.modal_engine_config import (
    ModalEngineConfig,
)
from superlinked.framework.common.space.embedding.model_based.singleton_embedding_engine_manager import (
    SingletonEmbeddingEngineManager,
)
from superlinked.framework.common.util.async_util import AsyncUtil
from superlinked.framework.common.util.image_util import PILImage
from superlinked.framework.dsl.space.image_space_field_set import (
    ImageDescriptionSpaceFieldSet,
    ImageSpaceFieldSet,
)
from superlinked.framework.dsl.space.space import Space

logger = structlog.getLogger()


class ImageSpace(Space[Vector, ImageData]):
    """
    Initialize the ImageSpace instance for generating vector representations
    from images, supporting models from the SentenceTransformers and OpenCLIP projects.
    """

    def __init__(
        self,
        image: Blob | DescribedBlob | None | Sequence[Blob | DescribedBlob | None],
        model: str = "clip-ViT-B-32",
        model_cache_dir: Path | None = None,
        model_handler: ModelHandler = ModelHandler.SENTENCE_TRANSFORMERS,
        embedding_engine_config: EmbeddingEngineConfig | None = None,
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
            embedding_engine_config (EmbeddingEngineConfig, optional): Configuration for the embedding engine.
                Defaults to EmbeddingEngineConfig().

        Raises:
            InvalidInputException: If the image and description fields are not
                from the same schema.
        """
        if embedding_engine_config is None:
            embedding_engine_config = EmbeddingEngineConfig()
        non_none_image: list[Blob | DescribedBlob] = self._fields_to_non_none_sequence(image)
        self.__validate_field_schemas(non_none_image)
        self.__validate_model_handler(model_handler, embedding_engine_config)
        image_fields, description_fields = self._split_images_from_descriptions(non_none_image)
        super().__init__(image_fields, Blob)
        length = AsyncUtil.run(
            SingletonEmbeddingEngineManager().calculate_length(
                model_handler, model, model_cache_dir, embedding_engine_config
            )
        )
        self.image = ImageSpaceFieldSet(self, set(image_fields), allowed_param_types=[str, PILImage])
        self.description = ImageDescriptionSpaceFieldSet(
            self,
            set(description for description in description_fields if description is not None),
            allowed_param_types=[str],
        )
        self._all_fields = self.image.fields | self.description.fields
        self._transformation_config = self._init_transformation_config(
            model, model_cache_dir, model_handler, length, embedding_engine_config
        )
        self.__embedding_node_by_schema = self._init_embedding_node_by_schema(
            image_fields, description_fields, self._all_fields, self.transformation_config
        )
        self._model = model

    def __validate_field_schemas(self, images: Blob | DescribedBlob | Sequence[Blob | DescribedBlob]) -> None:
        if any(
            image.description.schema_obj != image.blob.schema_obj
            for image in (images if isinstance(images, Sequence) else [images])
            if isinstance(image, DescribedBlob)
        ):
            raise InvalidInputException("ImageSpace image and description field must be in the same schema.")

    def __validate_model_handler(
        self, model_handler: ModelHandler, embedding_engine_config: EmbeddingEngineConfig
    ) -> None:
        if model_handler == ModelHandler.MODAL and not isinstance(embedding_engine_config, ModalEngineConfig):
            raise InvalidInputException(
                (
                    f"When using {ModelHandler.MODAL} as model_handler, embedding_engine_config must "
                    f"be an instance of ModalEngineConfig, but got {type(embedding_engine_config).__name__}"
                )
            )

    def _split_images_from_descriptions(
        self, images: Sequence[Blob | DescribedBlob]
    ) -> tuple[list[Blob], list[String | None]]:
        blobs, descriptions = zip(
            *[
                (image.blob, image.description) if isinstance(image, DescribedBlob) else (image, None)
                for image in images
            ]
        )
        return list(blobs), list(descriptions)

    @property
    @override
    def transformation_config(self) -> TransformationConfig[Vector, ImageData]:
        return self._transformation_config

    @property
    @override
    def _embedding_node_by_schema(
        self,
    ) -> dict[IdSchemaObject, EmbeddingNode[Vector, ImageData]]:
        return self.__embedding_node_by_schema

    @override
    def _create_default_node(self, schema: IdSchemaObject) -> EmbeddingNode[Vector, ImageData]:
        return ImageEmbeddingNode(None, None, self._transformation_config, self._all_fields, schema)

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
        self,
        model: str,
        model_cache_dir: Path | None,
        model_handler: ModelHandler,
        length: int,
        embedding_engine_config: EmbeddingEngineConfig,
    ) -> TransformationConfig[Vector, ImageData]:
        embedding_config = ImageEmbeddingConfig(
            ImageData,
            model,
            model_cache_dir,
            length,
            embedding_engine_config,
            model_handler,
        )
        aggregation_config = VectorAggregationConfig(Vector)
        normalization_config = L2NormConfig()
        return TransformationConfig(normalization_config, aggregation_config, embedding_config)

    def _init_embedding_node_by_schema(
        self,
        image_fields: Sequence[Blob],
        description_fields: Sequence[String | None],
        all_fields: set[SchemaField],
        transformation_config: TransformationConfig[Vector, ImageData],
    ) -> dict[IdSchemaObject, EmbeddingNode[Vector, ImageData]]:
        return {
            image_field.schema_obj: ImageEmbeddingNode(
                image_blob_node=SchemaFieldNode(image_field),
                description_node=SchemaFieldNode(description_field) if description_field is not None else None,
                transformation_config=transformation_config,
                fields_for_identification=all_fields,
            )
            for image_field, description_field in zip(image_fields, description_fields)
        }

    @override
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ImageSpace)
            and self.transformation_config == other.transformation_config
            and self.image.fields == other.image.fields
            and self.description.fields == other.description.fields
        )

    @override
    def __hash__(self) -> int:
        return hash((self.transformation_config, frozenset(self.image.fields), frozenset(self.description.fields)))
