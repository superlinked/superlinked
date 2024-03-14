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

from typing import Generic

from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.schema.schema_object import SchemaObjectT
from superlinked.framework.common.source.types import SourceTypeT
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.source.source import Source
from superlinked.framework.online.source.in_memory_source import (
    InMemorySource as CommonInMemorySource,
)


class RestSource(Source, Generic[SchemaObjectT, SourceTypeT]):
    def __init__(
        self,
        schema: SchemaObjectT,
        parser: DataParser | None = None,
        rest_descriptor: RestDescriptor | None = None,
    ):
        self.__schema = schema
        self.__parser = parser
        self._online_source: InMemorySource = InMemorySource(
            self.__schema, self.__parser
        )
        self.__rest_descriptor = rest_descriptor
        self.__path = (
            self.__rest_descriptor.source_path
            if self.__rest_descriptor and self.__rest_descriptor.source_path
            else self.__schema._schema_name
        )

    @property
    def _source(self) -> CommonInMemorySource:
        return self._online_source._source

    @property
    def path(self) -> str:
        return self.__path
