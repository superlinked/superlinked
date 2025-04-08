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

from attr import dataclass


@dataclass(frozen=True)
class Constants:
    MAX_DAG_DEPTH: int = 20
    DEFAULT_WEIGHT: float = 1.0
    DEFAULT_NOT_AFFECTING_WEIGHT: float = 0.0
    DEFAULT_NOT_AFFECTING_EMBEDDING_VALUE: float = 0.0
    DEFAULT_LIMIT: int = -1
    RADIUS_MIN: int = 0
    RADIUS_MAX: int = 1
    REDIS_TIMEOUT: int = 10000  # ms
    EFFECT_COUNT_KEY = "effect_count"
    EFFECT_OLDEST_TS_KEY = "effect_oldest_age"
    EFFECT_AVG_TS_KEY = "average_age"


constants = Constants()

__all__ = ["Constants", "constants"]
