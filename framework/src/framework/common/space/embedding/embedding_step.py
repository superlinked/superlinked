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

from beartype.typing import Any, Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingInputT,
)
from superlinked.framework.common.space.embedding.embedding import (
    Embedding,
    InvertibleEmbedding,
)
from superlinked.framework.common.transform.transform import Step


class EmbeddingStep(Generic[EmbeddingInputT], Step[EmbeddingInputT, Vector]):
    def __init__(self, embedding: Embedding[EmbeddingInputT, Any]) -> None:
        super().__init__()
        self._embedding = embedding

    @override
    def transform(
        self,
        input_: EmbeddingInputT,
        context: ExecutionContext,
    ) -> Vector:
        return self._embedding.embed(input_, context)


class MultiEmbeddingStep(
    Generic[EmbeddingInputT], Step[Sequence[EmbeddingInputT], Sequence[Vector]]
):
    def __init__(self, embedding: Embedding[EmbeddingInputT, Any]) -> None:
        super().__init__()
        self._embedding = embedding

    @override
    def transform(
        self,
        input_: Sequence[EmbeddingInputT],
        context: ExecutionContext,
    ) -> Sequence[Vector]:
        return self._embedding.embed_multiple(input_, context)


class InverseEmbeddingStep(Generic[EmbeddingInputT], Step[Vector, EmbeddingInputT]):
    def __init__(self, embedding: InvertibleEmbedding[EmbeddingInputT, Any]) -> None:
        super().__init__()
        self._embedding = embedding

    @override
    def transform(
        self,
        input_: Vector,
        context: ExecutionContext,
    ) -> EmbeddingInputT:
        return self._embedding.inverse_embed(input_, context)


class InverseMultiEmbeddingStep(
    Generic[EmbeddingInputT], Step[list[Vector], Sequence[EmbeddingInputT]]
):
    def __init__(self, embedding: InvertibleEmbedding[EmbeddingInputT, Any]) -> None:
        super().__init__()
        self._embedding = embedding

    @override
    def transform(
        self,
        input_: list[Vector],
        context: ExecutionContext,
    ) -> Sequence[EmbeddingInputT]:
        return self._embedding.inverse_embed_multiple(input_, context)
