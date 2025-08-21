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
from collections.abc import Sequence

from beartype.typing import Mapping

from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage_manager.entity_data_request import (
    EntityDataRequest,
    NodeResultRequest,
)
from superlinked.framework.common.storage_manager.node_info import NodeInfo
from superlinked.framework.common.storage_manager.storage_manager import StorageManager


class OnlineEntityCache:
    """Storage of data during online DAG evaluation, reducing database operations"""

    def __init__(self, storage_manager: StorageManager) -> None:
        self._cache: dict[EntityId, dict[str, NodeInfo]] = defaultdict(defaultdict)
        self._change: dict[EntityId, dict[str, NodeInfo]] = defaultdict(defaultdict)
        self._entity_to_origin: dict[EntityId, str] = {}
        self._storage_manager = storage_manager

    @property
    def changes(self) -> Mapping[EntityId, Mapping[str, NodeInfo]]:
        return self._change

    @property
    def origin_ids(self) -> Mapping[EntityId, str]:
        return self._entity_to_origin

    def load_node_info_into_cache(self, entity_info: Mapping[EntityId, Mapping[str, NodeInfo]]) -> None:
        self._cache.update(
            {entity_id: dict(node_id_to_node_info) for entity_id, node_id_to_node_info in entity_info.items()}
        )

    def set_node_info(self, entity_id: EntityId, node_id: str, node_info: NodeInfo) -> None:
        cached_node_info = self._cache.get(entity_id, {}).get(node_id)
        delta = self._calculate_node_info(cached_node_info, node_info, diff=True)
        if delta.result is None and not delta.data:
            return

        self._cache[entity_id][node_id] = self._calculate_node_info(cached_node_info, delta, diff=False)
        previous_change = self._change.get(entity_id, {}).get(node_id)
        self._change[entity_id][node_id] = self._calculate_node_info(previous_change, delta, diff=False)

    def set_origin(self, entity_id: EntityId, origin_id: str) -> None:
        self._entity_to_origin[entity_id] = origin_id

    async def get_node_results(
        self, entity_ids: Sequence[EntityId], node_id: str, node_data_type: type[NodeDataTypes]
    ) -> dict[EntityId, NodeDataTypes | None]:
        cached_results: dict[EntityId, NodeDataTypes | None] = {}
        entities_to_load: list[EntityId] = []

        for entity_id in entity_ids:
            if cached_node_info := self._cache[entity_id].get(node_id):
                cached_results[entity_id] = cached_node_info.result
            else:
                entities_to_load.append(entity_id)
        if entities_to_load:
            entity_data_requests = [
                EntityDataRequest(entity_id, [NodeResultRequest(node_id, node_data_type)])
                for entity_id in entities_to_load
            ]
            stored_entities = await self._storage_manager.read_entity_data_requests(entity_data_requests)
            batch_entity_info = dict(zip(entities_to_load, stored_entities))
            self.load_node_info_into_cache(batch_entity_info)
            for entity_id, stored_entity in batch_entity_info.items():
                cached_results[entity_id] = stored_entity[node_id].result if node_id in stored_entity else None
        return cached_results

    def get_node_data(self, entity_id: EntityId, node_id: str, field_name: str) -> NodeDataTypes | None:
        if initial_node_info := self._cache[entity_id].get(node_id):
            return initial_node_info.data.get(field_name)
        return None

    @staticmethod
    def _calculate_node_info(base_node_info: NodeInfo | None, new_node_info: NodeInfo, diff: bool) -> NodeInfo:
        def calculate_field_delta(
            base_field: NodeDataTypes | None, new_field: NodeDataTypes | None
        ) -> NodeDataTypes | None:
            return None if base_field == new_field or new_field is None else new_field

        def calculate_merged_field(
            base_field: NodeDataTypes | None, new_field: NodeDataTypes | None
        ) -> NodeDataTypes | None:
            return base_field if new_field is None else new_field

        if base_node_info is None:
            return new_node_info

        calculate_field_method = calculate_field_delta if diff else calculate_merged_field
        node_result = calculate_field_method(base_node_info.result, new_node_info.result)
        node_data_keys = set(base_node_info.data.keys()).union(new_node_info.data.keys())
        node_data = {
            node_data_key: new_data
            for node_data_key in node_data_keys
            if (
                new_data := calculate_field_method(
                    base_node_info.data.get(node_data_key), new_node_info.data.get(node_data_key)
                )
            )
            is not None
        }
        return NodeInfo(node_result, node_data)
