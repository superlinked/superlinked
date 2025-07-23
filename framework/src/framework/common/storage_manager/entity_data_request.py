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

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass

from beartype.typing import Sequence, cast
from typing_extensions import override

from superlinked.framework.common.data_types import NodeDataTypes, PythonTypes
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage_manager.entity_builder import EntityBuilder


@dataclass(frozen=True)
class NodeRequest(ABC):
    node_id: str

    @abstractmethod
    def to_field(self, entity_builder: EntityBuilder) -> Field: ...


@dataclass(frozen=True)
class NodeResultRequest(NodeRequest):
    data_type: type[NodeDataTypes]

    @override
    def to_field(self, entity_builder: EntityBuilder) -> Field:
        return entity_builder.compose_field(self.node_id, self.data_type)


@dataclass(frozen=True)
class NodeDataRequest(NodeRequest):
    field_name: str
    data_type: type[NodeDataTypes]

    @override
    def to_field(self, entity_builder: EntityBuilder) -> Field:
        return entity_builder.compose_field_from_node_data_descriptor(
            self.node_id, self.field_name, cast(type[PythonTypes], self.data_type)
        )


@dataclass(frozen=True)
class EntityDataRequest:
    """Represents a request to retrieve specific node result and data fields for an entity"""

    entity_id: EntityId
    node_requests: Sequence[NodeRequest]

    @classmethod
    def merge(cls, entity_data_requests: Sequence[EntityDataRequest]) -> list[EntityDataRequest]:
        id_to_requests: dict[EntityId, list[EntityDataRequest]] = defaultdict(list)
        for entity_data_request in entity_data_requests:
            id_to_requests[entity_data_request.entity_id].append(entity_data_request)
        return [
            EntityDataRequest(
                entity_id=id_,
                node_requests=list(set(node_request for request in requests for node_request in request.node_requests)),
            )
            for id_, requests in id_to_requests.items()
        ]
