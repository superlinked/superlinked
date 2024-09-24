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

from beartype.typing import Any, Generic, cast

from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.json_parser import JsonParser
from superlinked.framework.common.schema.id_schema_object import IdSchemaObjectT
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.online.source.online_source import OnlineSource


class RestSource(
    OnlineSource[IdSchemaObjectT, dict[str, Any]], Generic[IdSchemaObjectT]
):
    def __init__(
        self,
        schema: IdSchemaObjectT,
        parser: DataParser | None = None,
        rest_descriptor: RestDescriptor | None = None,
    ):
        super().__init__(
            schema,
            cast(
                DataParser[IdSchemaObjectT, dict[str, Any]],
                parser or JsonParser(schema),
            ),
        )
        self.__rest_descriptor = rest_descriptor
        self.__path = (
            self.__rest_descriptor.source_path
            if self.__rest_descriptor and self.__rest_descriptor.source_path
            else self._schema._schema_name
        )

    @property
    def path(self) -> str:
        return self.__path
