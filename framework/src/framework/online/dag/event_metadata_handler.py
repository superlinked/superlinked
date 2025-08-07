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

import math
from dataclasses import dataclass

from beartype.typing import Mapping

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage_manager.node_info import NodeInfo
from superlinked.framework.online.online_entity_cache import OnlineEntityCache


@dataclass(frozen=True)
class EventMetadata:
    effect_count: int
    effect_avg_ts: int
    effect_oldest_ts: int


class EventMetadataHandler:
    def __init__(self, metadata_key: str) -> None:
        self._metadata_key = metadata_key

    def recalculate(
        self, created_at: int, number_of_weights: int, stored_event_metadata: EventMetadata
    ) -> EventMetadata:
        recalculated_effect_count = stored_event_metadata.effect_count + number_of_weights
        recalculated_avg_ts = self._calculate_avg_ts(
            stored_event_metadata.effect_avg_ts, created_at, recalculated_effect_count, number_of_weights
        )
        recalculated_oldest_ts = self._calculate_oldest_ts(stored_event_metadata.effect_oldest_ts, created_at)
        return EventMetadata(recalculated_effect_count, recalculated_avg_ts, recalculated_oldest_ts)

    def _calculate_avg_ts(
        self, previous_avg_ts: int, created_at: int, recalculated_effect_count: int, new_effect_count: int
    ) -> int:
        if previous_avg_ts and new_effect_count == 0:
            return previous_avg_ts
        return math.ceil(  # ceil is used in case they are 1s apart
            (previous_avg_ts * (recalculated_effect_count - new_effect_count) + created_at * new_effect_count)
            / recalculated_effect_count
        )

    def _calculate_oldest_ts(self, previous_oldest_ts: int, created_at: int) -> int:
        return min(previous_oldest_ts, created_at) if previous_oldest_ts else created_at

    def read(self, schema: IdSchemaObject, object_id: str, online_entity_cache: OnlineEntityCache) -> EventMetadata:
        def get_event_metadata_item(object_id: str, field_name: str) -> int:
            entity_id = EntityId(schema_id=schema._schema_name, object_id=object_id)
            event_metadata_item = (
                online_entity_cache.get_node_data(
                    entity_id=entity_id, node_id=self._metadata_key, field_name=field_name
                )
                or 0
            )
            if not isinstance(event_metadata_item, int):
                raise InvalidStateException(
                    f"{field_name} must be int.",
                    actual_type=type(event_metadata_item).__name__,
                )
            return event_metadata_item

        return EventMetadata(
            effect_count=get_event_metadata_item(object_id, constants.EFFECT_COUNT_KEY),
            effect_avg_ts=get_event_metadata_item(object_id, constants.EFFECT_AVG_TS_KEY),
            effect_oldest_ts=get_event_metadata_item(object_id, constants.EFFECT_OLDEST_TS_KEY),
        )

    def write(
        self,
        schema: IdSchemaObject,
        event_metadata_items: Mapping[str, EventMetadata],
        online_entity_cache: OnlineEntityCache,
    ) -> None:
        for object_id, metadata in event_metadata_items.items():
            online_entity_cache.set_node_info(
                EntityId(schema_id=schema._schema_name, object_id=object_id),
                self._metadata_key,
                NodeInfo(
                    data={
                        constants.EFFECT_COUNT_KEY: metadata.effect_count,
                        constants.EFFECT_AVG_TS_KEY: metadata.effect_avg_ts,
                        constants.EFFECT_OLDEST_TS_KEY: metadata.effect_oldest_ts,
                    }
                ),
            )
