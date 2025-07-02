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

from __future__ import annotations

from dataclasses import dataclass

from superlinked.framework.common.settings import ResourceSettings


@dataclass(frozen=True)
class QueryUserConfig:
    with_metadata: bool = False
    redis_hybrid_policy: str | None = ResourceSettings().vector_database.REDIS_DEFAULT_HYBRID_POLICY
    redis_batch_size: int | None = ResourceSettings().vector_database.REDIS_DEFAULT_BATCH_SIZE
