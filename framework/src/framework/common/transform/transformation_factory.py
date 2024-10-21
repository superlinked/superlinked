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

from beartype.typing import Sequence, cast

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.weighted import Weighted
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
from superlinked.framework.common.space.embedding.embedding import InvertibleEmbedding
from superlinked.framework.common.space.embedding.embedding_factory import (
    EmbeddingFactory,
)
from superlinked.framework.common.space.embedding.embedding_step import (
    EmbeddingStep,
    InverseMultiEmbeddingStep,
    MultiEmbeddingStep,
)
from superlinked.framework.common.space.normalization.normalization_factory import (
    NormalizationFactory,
)
from superlinked.framework.common.space.normalization.normalization_step import (
    MultiNormalizationStep,
    NormalizationStep,
)
from superlinked.framework.common.transform.exception import (
    TransformationConfigurationException,
)
from superlinked.framework.common.transform.skip_weighting_wrapper import (
    SkipWeightingWrapper,
)
from superlinked.framework.common.transform.transform import Step


class TransformationFactory:
    @staticmethod
    def create_embedding_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT]
    ) -> Step[EmbeddingInputT, Vector]:
        embedding = EmbeddingFactory.create_embedding(
            transformation_config.embedding_config
        )
        normalization = NormalizationFactory.create_normalization(
            transformation_config.normalization_config
        )
        return EmbeddingStep(embedding).combine(NormalizationStep(normalization))

    @staticmethod
    def create_multi_embedding_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT]
    ) -> Step[Sequence[EmbeddingInputT], list[Vector]]:
        embedding = EmbeddingFactory.create_embedding(
            transformation_config.embedding_config
        )
        normalization = NormalizationFactory.create_normalization(
            transformation_config.normalization_config
        )
        return MultiEmbeddingStep(embedding).combine(
            MultiNormalizationStep(normalization)
        )

    @staticmethod
    def create_aggregation_transformation(
        transformation_config: TransformationConfig[AggregationInputT, EmbeddingInputT],
    ) -> Step[Sequence[Weighted[Vector]], Vector]:
        aggregation = AggregationFactory.create_aggregation(
            transformation_config.aggregation_config
        )
        aggregation_step = AggregationStep(aggregation)
        embedding = EmbeddingFactory.create_embedding(
            transformation_config.embedding_config
        )
        normalization = NormalizationFactory.create_normalization(
            transformation_config.normalization_config
        )
        transformation: Step[Sequence[Weighted[Vector]], Vector]
        if (
            isinstance(embedding, InvertibleEmbedding)
            and embedding.needs_inversion_before_aggregation
        ):
            if (
                transformation_config.embedding_config.embedding_input_type
                is not transformation_config.aggregation_config.aggregation_input_type
            ):
                raise TransformationConfigurationException(
                    "Cannot create aggregation step using an embedding with a different input type. "
                    + f"Got {transformation_config.embedding_config}"
                )
            inverse_multi_normalization_step = MultiNormalizationStep(
                normalization, denormalize=True
            )
            inverse_multi_embedding_step = InverseMultiEmbeddingStep(embedding)
            embedding_step = EmbeddingStep(embedding)
            skip_weighting_wrapper = SkipWeightingWrapper(
                inverse_multi_normalization_step.combine(inverse_multi_embedding_step)
            )
            transformation = skip_weighting_wrapper.combine(aggregation_step).combine(
                embedding_step
            )
        else:
            if (
                transformation_config.aggregation_config.aggregation_input_type
                is not Vector
            ):
                raise TransformationConfigurationException(
                    "Cannot create aggregation step without an invertible embedding. "
                    + f"Got {transformation_config.embedding_config}"
                )
            transformation = cast(
                Step[Sequence[Weighted[Vector]], Vector], aggregation_step
            )
        return transformation.combine(NormalizationStep(normalization))
