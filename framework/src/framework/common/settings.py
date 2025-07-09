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


import structlog
from beartype.typing import Any
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from typing_extensions import override

logger = structlog.getLogger()

YAML_FILENAME = "config.yaml"
FRAMEWORK_SECTION = "framework"
RESOURCE_SECTION = "resource"


class YamlBasedSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        try:
            return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls), file_secret_settings)
        except (FileNotFoundError, KeyError) as e:
            logger.debug("YAML configuration not available, falling back to dotenv", error=e)
            return (init_settings, env_settings, dotenv_settings, file_secret_settings)


class Settings(YamlBasedSettings):
    """Common settings"""

    APP_ID: str = "default"
    # Embedding specific settings
    ENABLE_MPS: bool = False
    SUPERLINKED_RESIZE_IMAGES: bool = False
    # Embedding specific settings - model
    MODEL_CACHE_DIR: str | None = None
    MODEL_LOCK_TIMEOUT_SECONDS: int = 120
    SENTENCE_TRANSFORMERS_MODEL_LOCK_MAX_RETRIES: int = 10
    SENTENCE_TRANSFORMERS_MODEL_LOCK_RETRY_DELAY: int = 1
    SENTENCE_TRANSFORMERS_MODEL_LOCK_TIMEOUT_BUFFER_SECONDS: int = 10
    SENTENCE_TRANSFORMERS_MODEL_LOCK_TIMEOUT_MIN_SECONDS: int = 5
    HUGGING_FACE_API_TOKEN: str | None = None  # TODO FAB-3560 - secret
    # Embedding specific settings - modal
    MODAL_APP_NAME: str = "App"
    MODAL_CLASS_NAME: str = "Embedder"
    MODAL_ENVIRONMENT_NAME: str = "main"
    MODAL_IMAGE_FORMAT: str | None = "WebP"
    MODAL_IMAGE_QUALITY: int = 95
    MODAL_BATCH_SIZE: int = 5000
    MODAL_MAX_RETRIES: int = 10
    MODAL_RETRY_DELAY: float = 0.2
    # Blob loading settings
    SUPERLINKED_CONCURRENT_BLOB_LOADING: bool = True
    BLOB_HANDLER_MODULE_PATH: str | None = None
    BLOB_HANDLER_CLASS_NAME: str | None = None
    BLOB_HANDLER_CLASS_ARGS: dict[str, Any] | None = None
    REQUEST_TIMEOUT: int = 600  # 10min
    # Logging specific params
    SUPERLINKED_LOG_LEVEL: int | str | None = None
    SUPERLINKED_LOG_AS_JSON: bool = False
    SUPERLINKED_LOG_FILE_PATH: str | None = None
    SUPERLINKED_EXPOSE_PII: bool = False
    DISABLE_RICH_TRACEBACK: bool = False
    # DAG visualization
    ENABLE_DAG_VISUALIZATION: bool = False
    DAG_VISUALIZATION_OUTPUT_DIR: str | None = None

    """Online settings"""
    ONLINE_PUT_CHUNK_SIZE: int = 10000
    ONLINE_EVENT_AGGREGATION_NODE_MAX_RETRY_COUNT: int = 5
    SUPERLINKED_CONCURRENT_EFFECT_EVALUATION: bool = True
    SUPERLINKED_CONCURRENT_ONLINE_DAG_EVALUATION: bool = False

    """Query settings"""
    QUERY_TO_RETURN_ORIGIN_ID: bool = False
    # NLQ specific params
    SUPERLINKED_NLQ_MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(
        yaml_file=YAML_FILENAME, yaml_config_section=FRAMEWORK_SECTION, extra="ignore", frozen=True
    )

    @override
    def model_post_init(self, __context: Any, /) -> None:
        self.__warn_for_incomplete_blob_params()

    def __warn_for_incomplete_blob_params(self) -> None:
        blob_params = {
            "BLOB_HANDLER_MODULE_PATH": self.BLOB_HANDLER_MODULE_PATH,
            "BLOB_HANDLER_CLASS_NAME": self.BLOB_HANDLER_CLASS_NAME,
            "BLOB_HANDLER_CLASS_ARGS": self.BLOB_HANDLER_CLASS_ARGS,
        }
        if any(value is not None for value in blob_params.values()) and not all(
            value is not None for value in blob_params.values()
        ):
            logger.warning(
                "Blob handler configuration warning: Incomplete blob handler parameters detected. "
                "Ensure all parameters are set for proper blob handler functionality.",
                params=blob_params,
            )


class ExternalMessageBusSettings(BaseModel):
    QUEUE_MODULE_PATH: str | None = None
    QUEUE_CLASS_NAME: str | None = None
    QUEUE_CLASS_ARGS: dict[str, Any] | None = None
    INGESTION_TOPIC_NAME: str | None = None
    QUEUE_MESSAGE_VERSION: int = 1

    @override
    def model_post_init(self, __context: Any, /) -> None:
        self.__warn_for_incomplete_queue_params()

    def __warn_for_incomplete_queue_params(self) -> None:
        queue_params = {
            "QUEUE_MODULE_PATH": self.QUEUE_MODULE_PATH,
            "QUEUE_CLASS_NAME": self.QUEUE_CLASS_NAME,
            "QUEUE_CLASS_ARGS": self.QUEUE_CLASS_ARGS,
            "INGESTION_TOPIC_NAME": self.INGESTION_TOPIC_NAME,
        }
        if any(value is not None for value in queue_params.values()) and any(
            value is None for value in queue_params.values()
        ):
            logger.warning(
                "Queue configuration warning: Incomplete queue parameters detected. "
                "Ensure all parameters are set for proper queue functionality.",
                params=queue_params,
            )


class VectorDatabaseSettings(BaseModel):
    INIT_SEARCH_INDICES: bool = True
    # Redis specific params
    REDIS_MAX_CONNECTIONS: int = 1600  # Good for 8 workers
    REDIS_SOCKET_TIMEOUT_SECONDS: float | None = 5.0
    REDIS_SOCKET_CONNECT_TIMEOUT_SECONDS: float | None = 2.0
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_DEFAULT_HYBRID_POLICY: str | None = None
    REDIS_DEFAULT_BATCH_SIZE: int | None = 250


class ResourceSettings(YamlBasedSettings):
    external_message_bus: ExternalMessageBusSettings = ExternalMessageBusSettings()
    vector_database: VectorDatabaseSettings = VectorDatabaseSettings()

    model_config = SettingsConfigDict(
        yaml_file=YAML_FILENAME, yaml_config_section=RESOURCE_SECTION, extra="ignore", frozen=True
    )


settings = Settings()
resource_settings = ResourceSettings()

__all__ = ["settings", "resource_settings"]
