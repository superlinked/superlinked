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

from typing import Any

from superlinked.batch.parser.spark_parser import SchemaMapper
from superlinked.framework.common.source.source import Source as CommonSource
from superlinked.framework.dsl.source.source import Source


class BatchSource(Source):
    def __init__(
        self,
        schema: Any,
        path: str,
    ) -> None:
        self.schema = schema
        self.path = path
        self.parser = SchemaMapper(self.schema)
        self.spark_schema = self.parser.map_schema()

    @property
    def _source(self) -> CommonSource:
        return self._source
