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

from superlinked.framework.common.data_types import Json
from superlinked.framework.common.observable import Subscriber
from superlinked.framework.common.parser.json_parser import JsonParser
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.storage.object_store_manager import (
    DataId,
    ObjectStoreManager,
)


class InMemoryObjectWriter(Subscriber[ParsedSchema]):
    def __init__(self, object_store_manager: ObjectStoreManager[Json]) -> None:
        super().__init__()
        self.__object_store_manager = object_store_manager

    def update(self, message: ParsedSchema) -> None:
        parser = JsonParser(message.schema)
        data = parser.marshal(message)
        data_id = DataId(message.schema._schema_name, message.id_)
        for data_element in data:
            self.__object_store_manager.save(data_id, data_element)
