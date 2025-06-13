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

from superlinked.framework.common.settings import Settings
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)


@dataclass(frozen=True)
class ModalEngineConfig(EmbeddingEngineConfig):  # pylint: disable=too-many-instance-attributes
    modal_app_name: str = Settings().MODAL_APP_NAME
    modal_class_name: str = Settings().MODAL_CLASS_NAME
    modal_environment_name: str = Settings().MODAL_ENVIRONMENT_NAME
    modal_batch_size: int = Settings().MODAL_BATCH_SIZE
    modal_max_retries: int = Settings().MODAL_MAX_RETRIES
    modal_retry_delay: float = Settings().MODAL_RETRY_DELAY
    modal_image_format: str | None = Settings().MODAL_IMAGE_FORMAT
    modal_image_quality: int = Settings().MODAL_IMAGE_QUALITY
