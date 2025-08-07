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

from beartype.typing import Generic, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.json_parser import JsonParser
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.source.types import SourceTypeT
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.online.source.online_source import OnlineSource


class InteractiveSource(OnlineSource[SourceTypeT], Generic[SourceTypeT]):
    """
    InteractiveSource represents a source of data, where you can put your data. This will supply
    the index with the data it needs to index and search in.
    """

    @TypeValidator.wrap
    def __init__(self, schema: IdSchemaObject, parser: DataParser[SourceTypeT] | None = None) -> None:
        """
        Initialize the InteractiveSource.

        Args:
            schema (IdSchemaObject): The schema object.
            parser (DataParser | None, optional): The data parser. Defaults to JsonParser if None is supplied.

        Raises:
            InvalidInputException: If the schema is not an instance of SchemaObject.
        """
        if not isinstance(schema, IdSchemaObject):
            raise InvalidInputException(f"Parameter `schema` is of invalid type: {schema.__class__.__name__}")

        super().__init__(schema, cast(DataParser[SourceTypeT], parser or JsonParser(schema)))
        self.__can_accept_data = False

    def allow_data_ingestion(self) -> None:
        self.__can_accept_data = True

    @override
    def put(self, data: SourceTypeT | Sequence[SourceTypeT]) -> None:
        """
        Put data into the InteractiveSource. This operation can take time as the vectorization
        of your data happens here.

        Args:
            data (SourceTypeT | list[SourceTypeT]): The data to put.
        """
        # Calls the parent, override is only necessary for adding the docstring.
        if not self.__can_accept_data:
            raise InvalidInputException(
                "Data ingestion is not allowed until executor.run() has been executed. "
                "Please ensure the executor is running before attempting to ingest data."
            )
        super().put(data)
