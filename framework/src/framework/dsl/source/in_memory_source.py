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

from beartype.typing import Generic

from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.json_parser import JsonParser
from superlinked.framework.common.schema.schema_object import (
    SchemaObject,
    SchemaObjectT,
)
from superlinked.framework.common.source.types import SourceTypeT
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.source.source import Source
from superlinked.framework.online.source.online_source import OnlineSource


class InMemorySource(Source, Generic[SchemaObjectT, SourceTypeT]):
    """
    InMemorySource represents a source of data, where you can put your data. This will supply
    the index with the data it needs to index and search in.
    """

    @TypeValidator.wrap
    def __init__(
        self,
        schema: SchemaObjectT,
        parser: DataParser | None = None,
    ) -> None:
        """
        Initialize the InMemorySource.

        Args:
            schema (IdSchemaObject): The schema object.
            parser (DataParser | None, optional): The data parser. Defaults to JsonParser if None is supplied.

        Raises:
            InitializationException: If the schema is not an instance of SchemaObject.
        """
        if not isinstance(schema, SchemaObject):
            raise InitializationException(
                f"Parameter `schema` is of invalid type: {schema.__class__.__name__}"
            )
        self._schema = schema
        self._parser = parser or JsonParser(schema)
        self.__source = OnlineSource(schema, self._parser)

    @property
    def _source(self) -> OnlineSource:
        return self.__source

    def put(self, data: list[SourceTypeT]) -> None:
        """
        Put data into the InMemorySource. This operation can take time as the vectorization
        of your data happens here.

        Args:
            data (list[SourceTypeT]): The data to put.
        """
        for item in data:
            self.__source.put(item)
