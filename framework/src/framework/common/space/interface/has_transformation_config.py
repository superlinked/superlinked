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

from abc import ABC, abstractmethod

from beartype.typing import Generic

from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingInputT,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)


class HasTransformationConfig(HasLength, Generic[AggregationInputT, EmbeddingInputT], ABC):
    @property
    @abstractmethod
    def transformation_config(
        self,
    ) -> TransformationConfig[AggregationInputT, EmbeddingInputT]:
        pass
