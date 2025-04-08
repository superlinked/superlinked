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

from beartype.typing import Mapping, Sequence

from superlinked.framework.common.const import constants
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager


@dataclass(frozen=True)
class EventMetadata:
    effect_count: int
    effect_avg_ts: int
    effect_oldest_ts: int


class EventMetadataHandler:
    def __init__(self, storage_manager: StorageManager, metadata_key: str) -> None:
        self._storage_manager = storage_manager
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

    def read(self, schema: SchemaObject, object_ids: Sequence[str]) -> dict[str, EventMetadata]:
        metadata_by_object_id = self._storage_manager.read_node_data(
            schema,
            object_ids,
            self._metadata_key,
            {constants.EFFECT_COUNT_KEY: int, constants.EFFECT_AVG_TS_KEY: int, constants.EFFECT_OLDEST_TS_KEY: int},
        )
        return {
            object_id: EventMetadata(
                metadata.get(constants.EFFECT_COUNT_KEY, 0),
                metadata.get(constants.EFFECT_AVG_TS_KEY, 0),
                metadata.get(constants.EFFECT_OLDEST_TS_KEY, 0),
            )
            for object_id, metadata in metadata_by_object_id.items()
        }

    def write(self, schema: SchemaObject, event_metadata_items: Mapping[str, EventMetadata]) -> None:
        node_data_by_object_id = {
            object_id: {
                constants.EFFECT_COUNT_KEY: event_metadata.effect_count,
                constants.EFFECT_AVG_TS_KEY: event_metadata.effect_avg_ts,
                constants.EFFECT_OLDEST_TS_KEY: event_metadata.effect_oldest_ts,
            }
            for object_id, event_metadata in event_metadata_items.items()
        }
        self._storage_manager.write_node_data(schema, node_data_by_object_id, self._metadata_key)
