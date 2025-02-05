# Copyright 2025 Superlinked, Inc
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

from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)
from superlinked.framework.common.space.embedding.embedding_factory import (
    EmbeddingFactory,
)
from superlinked.framework.common.transform.transform import Step


class TransformVectorToQueryVector(Step[Vector, Vector]):
    def __init__(self, embedding_config: EmbeddingConfig) -> None:
        super().__init__()
        self._embedding = EmbeddingFactory.create_embedding(embedding_config)

    @override
    def transform(
        self,
        input_: Vector,
        context: ExecutionContext,
    ) -> Vector:
        return self._embedding._to_query_vector(input_, context)
