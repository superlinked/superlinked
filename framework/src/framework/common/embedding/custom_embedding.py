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

from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.embedding.embedding import Embedding
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.normalization import Normalization


class CustomEmbedding(Embedding[list[float]], HasLength):
    def __init__(self, length: int, normalization: Normalization) -> None:
        self.__length: int = length
        self._normalization: Normalization = normalization

    @override
    def embed(
        self,
        input_: list[float],
        context: ExecutionContext,  # pylint: disable=unused-argument
    ) -> Vector:
        return self._normalization.normalize(Vector(input_))

    @property
    def length(self) -> int:
        return self.__length
