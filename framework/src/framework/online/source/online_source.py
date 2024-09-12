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

import structlog
from beartype.typing import Generic

from superlinked.framework.common.observable import Publisher
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.id_schema_object import IdSchemaObjectT
from superlinked.framework.common.schema.schema_object import SchemaObjectT
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.source.source import Source
from superlinked.framework.common.source.types import SourceTypeT
from superlinked.framework.common.util.collection_util import chunk_list

logger = structlog.get_logger()


class OnlineSource(
    Generic[IdSchemaObjectT, SourceTypeT],
    Publisher[ParsedSchema],
    Source[IdSchemaObjectT, SourceTypeT],
):
    def __init__(
        self, schema: SchemaObjectT, parser: DataParser[IdSchemaObjectT, SourceTypeT]
    ) -> None:
        Publisher.__init__(self)
        Source.__init__(self, schema)
        self.parser = parser
        self._logger = logger.bind(
            schema=schema._schema_name,
        )

    def put(self, data: SourceTypeT) -> None:
        parsed_schemas: list[ParsedSchema] = self.parser.unmarshal(data)
        chunk_size = Settings().ONLINE_PUT_CHUNK_SIZE
        put_logger = self._logger.bind(
            n_chunk_total=math.ceil(len(parsed_schemas) / chunk_size),
        )
        for i, batch in enumerate(
            chunk_list(data=parsed_schemas, chunk_size=chunk_size)
        ):
            self._dispatch(batch)
            put_logger.info(
                "processed chunk",
                n_chunk_current=i + 1,
            )
