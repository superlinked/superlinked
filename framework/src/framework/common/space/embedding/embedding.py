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

from beartype.typing import Any, Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_default_vector import HasDefaultVector
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfigT,
    EmbeddingInputT,
)


class Embedding(HasDefaultVector, Generic[EmbeddingInputT, EmbeddingConfigT], ABC):
    def __init__(self, embedding_config: EmbeddingConfigT) -> None:
        self._config = embedding_config

    @abstractmethod
    def embed(self, input_: EmbeddingInputT, context: ExecutionContext) -> Vector:
        pass

    def embed_multiple(
        self, inputs: Sequence[EmbeddingInputT], context: ExecutionContext
    ) -> list[Vector]:
        return [self.embed(input_, context) for input_ in inputs]

    @override
    def __eq__(self, other: Any) -> bool:
        if type(self) is type(other):
            return self._config == other._config
        return False

    @override
    def __hash__(self) -> int:
        return hash(self._config)

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__ if self.__dict__ else ''})"


class InvertibleEmbedding(
    Embedding[EmbeddingInputT, EmbeddingConfigT],
    Generic[EmbeddingInputT, EmbeddingConfigT],
    ABC,
):
    @abstractmethod
    def inverse_embed(
        self, vector: Vector, context: ExecutionContext
    ) -> EmbeddingInputT:
        pass

    @property
    @abstractmethod
    def needs_inversion_before_aggregation(self) -> bool:
        pass

    def inverse_embed_multiple(
        self, vectors: Sequence[Vector], context: ExecutionContext
    ) -> list[EmbeddingInputT]:
        return [self.inverse_embed(vector, context) for vector in vectors]
