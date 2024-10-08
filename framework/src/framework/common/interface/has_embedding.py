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

from abc import ABC, abstractmethod

from beartype.typing import Sequence

from superlinked.framework.common.embedding.embedding import Embedding


class HasEmbedding(ABC):
    @property
    @abstractmethod
    def embedding(self) -> Embedding:
        pass

    @staticmethod
    def get_common_embedding(objs_with_embedding: Sequence[HasEmbedding]) -> Embedding:
        if filtered_embeddings := {
            obj.embedding for obj in objs_with_embedding if obj.embedding is not None
        }:
            if len(filtered_embeddings) > 1:
                raise ValueError("Embeddings do not match.")
            return filtered_embeddings.pop()
        raise ValueError("No embedding is present.")
