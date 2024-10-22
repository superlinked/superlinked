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

from beartype.typing import Generic
from typing_extensions import override

from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationConfig,
    AggregationInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
    EmbeddingInputT,
)
from superlinked.framework.common.space.config.normalization.normalization_config import (
    NormalizationConfig,
)


@dataclass(frozen=True)
class TransformationConfig(HasLength, Generic[AggregationInputT, EmbeddingInputT]):
    normalization_config: NormalizationConfig
    aggregation_config: AggregationConfig[AggregationInputT]
    embedding_config: EmbeddingConfig[EmbeddingInputT]

    @property
    @override
    def length(self) -> int:
        return self.embedding_config.length
