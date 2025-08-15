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

from dataclasses import dataclass

from beartype.typing import Any, Generic, Sequence, cast

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.space.aggregation.aggregation import Aggregation
from superlinked.framework.common.space.aggregation.aggregation_factory import (
    AggregationFactory,
)
from superlinked.framework.common.space.aggregation.aggregation_step import (
    AggregationStep,
)
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingInputT,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.common.space.embedding.embedding import (
    Embedding,
    InvertibleEmbedding,
)
from superlinked.framework.common.space.embedding.embedding_factory import (
    EmbeddingFactory,
)
from superlinked.framework.common.space.embedding.embedding_step import (
    EmbeddingStep,
    InverseMultiEmbeddingStep,
    MultiEmbeddingStep,
)
from superlinked.framework.common.space.embedding.model_based.embedding_engine_manager import (
    EmbeddingEngineManager,
)
from superlinked.framework.common.space.embedding.model_based.singleton_embedding_engine_manager import (
    SingletonEmbeddingEngineManager,
)
from superlinked.framework.common.space.normalization.normalization import Normalization
from superlinked.framework.common.space.normalization.normalization_factory import (
    NormalizationFactory,
)
from superlinked.framework.common.space.normalization.normalization_step import (
    MultiNormalizationStep,
    NormalizationStep,
)
from superlinked.framework.common.transform.temp_lift_weighting_wrapper import (
    TempLiftWeightingWrapper,
)
from superlinked.framework.common.transform.transform import (
    FilterPredicate,
    Step,
    Transform,
)


@dataclass(frozen=True)
class BaseTransformations(Generic[AggregationInputT, EmbeddingInputT]):
    normalization: Normalization
    aggregation: Aggregation[AggregationInputT]
    embedding: Embedding[EmbeddingInputT, Any]


class TransformationFactory:
    @staticmethod
    def create_embedding_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT],
        embedding_engine_manager: EmbeddingEngineManager | None = None,
    ) -> Step[EmbeddingInputT, Vector]:
        if embedding_engine_manager is None:
            embedding_engine_manager = SingletonEmbeddingEngineManager()
        embedding = EmbeddingFactory.create_embedding(transformation_config.embedding_config, embedding_engine_manager)
        normalization = NormalizationFactory.create_normalization(transformation_config.normalization_config)
        return EmbeddingStep(embedding).combine(NormalizationStep(normalization))

    @staticmethod
    def create_multi_embedding_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT],
        embedding_engine_manager: EmbeddingEngineManager | None = None,
    ) -> Step[Sequence[EmbeddingInputT], list[Vector]]:
        if embedding_engine_manager is None:
            embedding_engine_manager = SingletonEmbeddingEngineManager()
        embedding = EmbeddingFactory.create_embedding(transformation_config.embedding_config, embedding_engine_manager)
        normalization = NormalizationFactory.create_normalization(transformation_config.normalization_config)
        return MultiEmbeddingStep(embedding).combine(MultiNormalizationStep(normalization))

    @staticmethod
    def create_aggregation_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT],
        embedding_engine_manager: EmbeddingEngineManager | None = None,
    ) -> Step[Sequence[Weighted[Vector]], Vector]:
        if embedding_engine_manager is None:
            embedding_engine_manager = SingletonEmbeddingEngineManager()
        base_transformations = TransformationFactory.__create_base_transformations(
            transformation_config, embedding_engine_manager
        )
        transformation: Step[Sequence[Weighted[Vector]], Vector]
        if (
            isinstance(base_transformations.embedding, InvertibleEmbedding)
            and base_transformations.embedding.needs_inversion_before_aggregation  # pylint: disable=no-member
        ):
            transformation = TransformationFactory.inverse_aggregation_transformation(
                transformation_config, base_transformations
            )
        else:
            if transformation_config.aggregation_config.aggregation_input_type is not Vector:
                raise InvalidStateException(
                    "Cannot create non-vector aggregation step without an invertible embedding.",
                    embedding_config=transformation_config.embedding_config,
                )
            aggregation_step = AggregationStep(base_transformations.aggregation)
            transformation = cast(
                Step[Sequence[Weighted[Vector]], Vector],
                aggregation_step.combine_if(
                    cast(Step[AggregationInputT, Vector], NormalizationStep(base_transformations.normalization)),
                    predicate=FilterPredicate(
                        base_transformations.aggregation.filter_predicate,
                        Vector.init_zero_vector(transformation_config.embedding_config.default_vector.dimension),
                    ),
                ),
            )
        return transformation

    @staticmethod
    def inverse_aggregation_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT],
        base_transformations: BaseTransformations[AggregationInputT, EmbeddingInputT],
    ) -> Transform[Sequence[Weighted[Vector]], Vector]:
        if not isinstance(base_transformations.embedding, InvertibleEmbedding):
            raise InvalidStateException(
                "Inverse aggregation cannot be initialized with given embedding.",
                embedding=base_transformations.embedding,
            )
        if (
            transformation_config.embedding_config.embedding_input_type
            is not transformation_config.aggregation_config.aggregation_input_type
        ):
            raise InvalidStateException(
                "Cannot create aggregation step using an embedding with a different input type.",
                embedding_config=transformation_config.embedding_config,
                aggregation_config=transformation_config.aggregation_config,
            )
        inverse_multi_normalization_step = MultiNormalizationStep(base_transformations.normalization, denormalize=True)
        inverse_multi_embedding_step = InverseMultiEmbeddingStep(base_transformations.embedding)
        temp_lift_weighting_wrapper = TempLiftWeightingWrapper(
            inverse_multi_normalization_step.combine(inverse_multi_embedding_step)
        )
        normalization_step = NormalizationStep(base_transformations.normalization)
        aggregation_step = AggregationStep(base_transformations.aggregation)
        embedding_step = EmbeddingStep(base_transformations.embedding)
        return temp_lift_weighting_wrapper.combine(
            aggregation_step.combine_if(
                embedding_step.combine(normalization_step),
                predicate=FilterPredicate(
                    filter_=base_transformations.aggregation.filter_predicate,
                    default_value=Vector.init_zero_vector(
                        transformation_config.embedding_config.default_vector.dimension
                    ),
                ),
            ),
        )

    @staticmethod
    def __create_base_transformations(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT],
        embedding_engine_manager: EmbeddingEngineManager,
    ) -> BaseTransformations[AggregationInputT, EmbeddingInputT]:
        normalization = NormalizationFactory.create_normalization(transformation_config.normalization_config)
        aggregation = AggregationFactory.create_aggregation(transformation_config.aggregation_config)
        embedding = EmbeddingFactory.create_embedding(transformation_config.embedding_config, embedding_engine_manager)
        return BaseTransformations(normalization, aggregation, embedding)
