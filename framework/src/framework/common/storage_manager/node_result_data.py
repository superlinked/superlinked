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


from dataclasses import dataclass

from superlinked.framework.common.data_types import NodeDataTypes


@dataclass(frozen=True)
class NodeResultData:
    """Represents node data with its associated schema and identifiers."""

    schema_id: str
    object_id: str
    node_id: str
    result: NodeDataTypes | None
    origin_id: str | None = None
