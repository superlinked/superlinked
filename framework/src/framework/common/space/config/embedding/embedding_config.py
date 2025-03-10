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
from dataclasses import dataclass

from beartype.typing import Any, Generic, TypeVar

from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.interface.has_default_vector import HasDefaultVector
from superlinked.framework.common.util.string_util import StringUtil

EmbeddingInputT = TypeVar("EmbeddingInputT", bound=NodeDataTypes)


@dataclass(frozen=True)
class EmbeddingConfig(HasDefaultVector, Generic[EmbeddingInputT], ABC):
    embedding_input_type: type[EmbeddingInputT]

    @abstractmethod
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        """
        This method should include all class members that define its functionality, excluding the parent(s).
        """

    def __str__(self) -> str:
        members = StringUtil.sort_and_serialize(self._get_embedding_config_parameters())
        return f"{type(self).__name__}(embedding_input_type={self.embedding_input_type.__name__}, {members})"


EmbeddingConfigT = TypeVar("EmbeddingConfigT", bound=EmbeddingConfig)
