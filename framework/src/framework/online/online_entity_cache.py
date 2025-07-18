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

from beartype.typing import Mapping

from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.storage.entity_key import EntityKey


class OnlineEntityCache:
    """Storage of data during online DAG evaluation, reducing database operations"""

    def __init__(self) -> None:
        self._cache: dict[EntityKey, dict[str, NodeDataTypes]] = {}
        self._changed_keys: dict[EntityKey, set[str]] = defaultdict(set[str])

    def get(self, entity_key: EntityKey, field_name: str) -> NodeDataTypes | None:
        return self._cache.get(entity_key, {}).get(field_name)

    def set(self, entity_key: EntityKey, field_name: str, node_data: NodeDataTypes) -> None:
        if entity_key not in self._cache:
            self._cache[entity_key] = {}

        if field_name not in self._cache[entity_key] or self._cache[entity_key][field_name] != node_data:
            self._changed_keys[entity_key].add(field_name)
        self._cache[entity_key][field_name] = node_data

    def set_multiple(self, entity_key: EntityKey, field_name_to_node_data: Mapping[str, NodeDataTypes]) -> None:
        for field_name, field_value in field_name_to_node_data.items():
            self.set(entity_key, field_name, field_value)

    def get_changed(self) -> Mapping[EntityKey, Mapping[str, NodeDataTypes]]:
        return {
            entity_key: {
                field_name: node_data
                for field_name, node_data in field_name_to_node_data.items()
                if field_name in self._changed_keys[entity_key]
            }
            for entity_key, field_name_to_node_data in self._cache.items()
            if entity_key in self._changed_keys
        }
