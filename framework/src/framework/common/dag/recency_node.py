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

from superlinked.framework.common.dag.embedding_node import InputEmbeddingNode
from superlinked.framework.common.embedding.recency_embedding import (
    RecencyEmbedding,
    RecencyEmbeddingConfig,
)


class RecencyNode(InputEmbeddingNode[int, RecencyEmbeddingConfig]):
    @property
    @override
    def embedding_type(self) -> type[RecencyEmbedding]:
        return RecencyEmbedding
