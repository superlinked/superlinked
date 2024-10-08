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

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    SERVER_URL: str
    APP_MODULE_PATH: str
    LOG_LEVEL: str
    PERSISTENCE_FOLDER_PATH: str
    DISABLE_RECENCY_SPACE: bool
    WORKER_COUNT: int

    JSON_LOG_FILE: str | None = None
    LOG_AS_JSON: bool = False
    EXPOSE_PII: bool = False

    model_config = SettingsConfigDict(env_file="executor/.env", extra="ignore")
