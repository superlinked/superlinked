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

from dataclasses import dataclass

from typing_extensions import override

from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)


@dataclass(frozen=True)
class ModalEngineConfig(EmbeddingEngineConfig):  # pylint: disable=too-many-instance-attributes
    token_id: str
    token_secret: str
    app_name: str = "App"
    class_name: str = "Embedder"
    environment_name: str = "main"
    batch_size: int = 5000
    max_retries: int = 10
    retry_delay: float = 0.2

    @override
    def __str__(self) -> str:
        attributes = [
            f"app_name={self.app_name}",
            f"class_name={self.class_name}",
            f"environment_name={self.environment_name}",
            f"batch_size={self.batch_size}",
            f"max_retries={self.max_retries}",
            f"retry_delay={self.retry_delay}",
        ]
        return f"{super().__str__()}, " + ", ".join(attributes)
