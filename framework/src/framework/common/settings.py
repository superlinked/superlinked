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


import json

import structlog
from beartype.typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import override

from superlinked.framework.common.util.singleton_decorator import singleton

logger = structlog.getLogger()


@singleton
class Settings(BaseSettings):
    ONLINE_PUT_CHUNK_SIZE: int = 10000
    GPU_EMBEDDING_THRESHOLD: int = 0
    DISABLE_RICH_TRACEBACK: bool = False
    SUPERLINKED_LOG_LEVEL: int | None = None
    SUPERLINKED_LOG_AS_JSON: bool = False
    SUPERLINKED_LOG_FILE_PATH: str | None = None
    SUPERLINKED_EXPOSE_PII: bool = False
    # QUEUE specific params
    QUEUE_MODULE_PATH: str | None = None
    QUEUE_CLASS_NAME: str | None = None
    QUEUE_CLASS_ARGS_STR: str | None = None
    QUEUE_CLASS_ARGS: dict[str, Any] | None = None
    INGESTION_TOPIC_NAME: str | None = None
    QUEUE_MESSAGE_VERSION: int = 1
    REQUEST_TIMEOUT: int = 600  # 10min

    model_config = SettingsConfigDict(env_file=".env")

    @override
    def model_post_init(self, __context: Any) -> None:
        self.__warn_if_none_queue_params()
        if self.QUEUE_CLASS_ARGS_STR:
            try:
                self.QUEUE_CLASS_ARGS = json.loads(  # pylint: disable=invalid-name
                    self.QUEUE_CLASS_ARGS_STR
                )
            except json.JSONDecodeError as e:
                logger.warning(e)

    def __warn_if_none_queue_params(self) -> None:
        queue_params = {
            "QUEUE_MODULE_PATH": self.QUEUE_MODULE_PATH,
            "QUEUE_CLASS_NAME": self.QUEUE_CLASS_NAME,
            "QUEUE_CLASS_ARGS_STR": self.QUEUE_CLASS_ARGS_STR,
            "INGESTION_TOPIC_NAME": self.INGESTION_TOPIC_NAME,
        }
        if any(value is not None for value in queue_params.values()) and not all(
            value is not None for value in queue_params.values()
        ):
            logger.warning(
                "Queue configuration warning: Incomplete queue parameters detected. "
                "Ensure all parameters are set for proper queue functionality.",
                params=queue_params,
            )
