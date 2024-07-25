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

from beartype.typing import Generic

from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.json_parser import JsonParser
from superlinked.framework.common.schema.schema_object import SchemaObjectT
from superlinked.framework.common.source.types import SourceTypeT
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.source.source import Source
from superlinked.framework.online.source.online_source import OnlineSource


class RestSource(Source, Generic[SchemaObjectT, SourceTypeT]):
    def __init__(
        self,
        schema: SchemaObjectT,
        parser: DataParser | None = None,
        rest_descriptor: RestDescriptor | None = None,
    ):
        self.__schema = schema
        self.__parser = parser or JsonParser(self.__schema)
        self._online_source = OnlineSource(self.__schema, self.__parser)
        self.__rest_descriptor = rest_descriptor
        self.__path = (
            self.__rest_descriptor.source_path
            if self.__rest_descriptor and self.__rest_descriptor.source_path
            else self.__schema._schema_name
        )

    @property
    def _source(self) -> OnlineSource:
        return self._online_source

    @property
    def path(self) -> str:
        return self.__path
