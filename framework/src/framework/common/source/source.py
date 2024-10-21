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

from beartype.typing import Generic, TypeVar

from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.schema.id_schema_object import IdSchemaObjectT
from superlinked.framework.common.source.types import SourceTypeT

SourceT = TypeVar("SourceT", bound="Source")


class Source(Generic[IdSchemaObjectT, SourceTypeT]):
    def __init__(
        self, schema: IdSchemaObjectT, parser: DataParser[IdSchemaObjectT, SourceTypeT]
    ) -> None:
        self._schema = schema
        self._parser: DataParser[IdSchemaObjectT, SourceTypeT] = parser

    @property
    def parser(self) -> DataParser[IdSchemaObjectT, SourceTypeT]:
        return self._parser
