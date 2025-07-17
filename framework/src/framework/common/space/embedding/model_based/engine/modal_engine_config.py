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
    modal_app_name: str = "App"
    modal_class_name: str = "Embedder"
    modal_environment_name: str = "main"
    modal_batch_size: int = 5000
    modal_max_retries: int = 10
    modal_retry_delay: float = 0.2
    modal_image_format: str | None = "WebP"
    modal_image_quality: int = 95

    @override
    def __str__(self) -> str:
        attributes = [
            f"modal_app_name={self.modal_app_name}",
            f"modal_class_name={self.modal_class_name}",
            f"modal_environment_name={self.modal_environment_name}",
            f"modal_batch_size={self.modal_batch_size}",
            f"modal_max_retries={self.modal_max_retries}",
            f"modal_retry_delay={self.modal_retry_delay}",
            f"modal_image_format={self.modal_image_format}",
            f"modal_image_quality={self.modal_image_quality}",
        ]
        return f"{super().__str__()}, " + ", ".join(attributes)
