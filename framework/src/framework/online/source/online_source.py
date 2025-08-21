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

import structlog
from beartype.typing import Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.observable import TransformerPublisher
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.settings import settings
from superlinked.framework.common.source.source import Source
from superlinked.framework.common.source.types import SourceTypeT
from superlinked.framework.common.util.async_util import AsyncUtil

logger = structlog.get_logger()


class OnlineSource(Generic[SourceTypeT], TransformerPublisher[SourceTypeT, ParsedSchema], Source[SourceTypeT]):
    def __init__(self, schema: IdSchemaObject, parser: DataParser[SourceTypeT]) -> None:
        TransformerPublisher.__init__(self, chunk_size=settings.ONLINE_PUT_CHUNK_SIZE)
        Source.__init__(self, schema, parser)
        self._logger = logger.bind(
            schema=schema._schema_name,
        )

    @override
    async def transform(self, message: SourceTypeT) -> list[ParsedSchema]:
        return await self.parser.unmarshal(message)

    def put(self, data: SourceTypeT | Sequence[SourceTypeT]) -> None:
        AsyncUtil.run(self.put_async(data))

    async def put_async(self, data: SourceTypeT | Sequence[SourceTypeT]) -> None:
        await self._dispatch(data)
