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
from beartype.typing import Mapping

from superlinked.framework.common.storage.entity.entity_id import EntityId


@dataclass(frozen=True)
class RedisKNNResult:
    entity_id: EntityId
    score: float
    field_name_to_data: Mapping[str, bytes]
