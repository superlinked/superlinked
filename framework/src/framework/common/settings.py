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

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

from superlinked.framework.common.util.singleton_decorator import singleton


@singleton
class Settings(BaseSettings):
    ONLINE_PUT_CHUNK_SIZE: int = 10000
    GPU_EMBEDDING_THRESHOLD: int = 0
    DISABLE_RICH_TRACEBACK: int = 0
    SUPERLINKED_LOG_LEVEL: int = logging.INFO
    LOG_FILE_PATH: str | None = None

    model_config = SettingsConfigDict(env_file=".env")
