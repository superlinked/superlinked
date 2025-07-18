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

from collections import defaultdict
from dataclasses import dataclass

from beartype.typing import Sequence

from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.storage.entity_key import EntityKey


@dataclass(frozen=True)
class EntityDataRequest:
    """Represents a request to retrieve specific node data fields for an entity"""

    entity_key: EntityKey
    node_data_name_to_type: dict[str, type[NodeDataTypes]]

    @staticmethod
    def merge(entity_data_requests: Sequence[EntityDataRequest]) -> list[EntityDataRequest]:
        entity_key_to_requests = defaultdict(list)
        for request in entity_data_requests:
            entity_key_to_requests[request.entity_key].append(request)

        return [
            EntityDataRequest(
                entity_key,
                {
                    node_data_name: type_
                    for request in requests
                    for node_data_name, type_ in request.node_data_name_to_type.items()
                },
            )
            for entity_key, requests in entity_key_to_requests.items()
        ]
