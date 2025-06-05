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


@dataclass(frozen=True)
class ModalConfig:  # pylint: disable=too-many-instance-attributes
    app_name: str = Settings().MODAL_APP_NAME
    class_name: str = Settings().MODAL_CLASS_NAME
    environment_name: str = Settings().MODAL_ENVIRONMENT_NAME
    batch_size: int = Settings().MODAL_BATCH_SIZE
    max_concurrent_batches: int = Settings().MODAL_MAX_CONCURRENT_BATCHES
    max_retries: int = Settings().MODAL_MAX_RETRIES
    retry_delay: float = Settings().MODAL_RETRY_DELAY
    image_format: str | None = Settings().MODAL_IMAGE_FORMAT
    image_quality: int = Settings().MODAL_IMAGE_QUALITY
