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

import asyncio

from beartype.typing import Any, Sequence, cast

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.event_schema_object import (
    EventSchemaObject,
    SchemaReference,
)
from superlinked.framework.common.schema.schema_object import SFT, Blob, SchemaField
from superlinked.framework.common.util.dot_separated_path_util import (
    DotSeparatedPathUtil,
    ValuedDotSeparatedPath,
)


class JsonParser(DataParser[dict[str, Any]]):
    """
    JsonParser gets a `Json` object and using `str` based dot separated path mapping
    it transforms the `Json` to a desired schema.
    """

    async def unmarshal(self, data: dict[str, Any] | Sequence[dict[str, Any]]) -> list[ParsedSchema]:
        """
        Parses the given Json into a list of ParsedSchema objects according to the defined schema and mapping.

        Args:
            data (Json): The Json representation of your data.

        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.
        """

        if isinstance(data, dict):
            data = [data]
        return await self._unmarshal_multiple(data)

    async def _unmarshal_multiple(self, json_datas: Sequence[dict[str, Any]]) -> list[ParsedSchema]:
        ids = [self.__ensure_id(json_data) for json_data in json_datas]

        parsed_values_for_each_field = await asyncio.gather(
            *[self._parse_schema_field_values(field, json_datas) for field in self._schema.schema_fields]
        )
        parsed_fields_for_each_field = [
            [
                ParsedSchemaField.from_schema_field(field, parsed_value)
                for parsed_value in parsed_values
                if parsed_value is not None
            ]
            for field, parsed_values in zip(self._schema.schema_fields, parsed_values_for_each_field)
        ]
        parsed_fields_for_each_data = self._transpose_parsed_fields(json_datas, parsed_fields_for_each_field)
        return [
            (
                EventParsedSchema(
                    self._schema,
                    id_,
                    fields,
                    self.__ensure_created_at(json_data),
                )
                if self._is_event_data_parser
                else ParsedSchema(self._schema, id_, fields)
            )
            for id_, fields, json_data in zip(ids, parsed_fields_for_each_data, json_datas)
        ]

    def _transpose_parsed_fields(
        self, json_datas: Sequence[dict[str, Any]], parsed_fields_for_each_field: Sequence[Sequence[ParsedSchemaField]]
    ) -> list[list[ParsedSchemaField]]:
        return [
            [field_list[data_idx] for field_list in parsed_fields_for_each_field if data_idx < len(field_list)]
            for data_idx in range(len(json_datas))
        ]

    def _marshal(self, parsed_schemas: Sequence[ParsedSchema]) -> list[dict[str, Any]]:
        """
        Converts a ParsedSchema objects back into a list of Json objects.
        You can use this functionality to check, if your mapping was defined properly.
        """
        return [
            self.__construct_json(list_of_schema_fields)
            for list_of_schema_fields in [
                self.__get_all_fields_from_parsed_schema(parsed_schema) for parsed_schema in parsed_schemas
            ]
        ]

    def __construct_json(self, parsed_schema_fields: list[ParsedSchemaField]) -> dict[str, Any]:
        altered_parsed_schema_fields = self._handle_parsed_schema_fields(parsed_schema_fields)
        return DotSeparatedPathUtil.to_dict(
            [
                ValuedDotSeparatedPath(
                    self._get_path(field.schema_field),
                    field.value,
                )
                for field in altered_parsed_schema_fields
            ]
        )

    def __ensure_id(self, data: dict[str, Any]) -> str:
        id_ = DotSeparatedPathUtil.get(data, self._id_name)
        if not self._is_id_value_valid(id_):
            raise InvalidInputException(
                "The mandatory id field has missing or has invalid type values in the input object."
            )
        return str(id_)

    def __ensure_created_at(self, data: dict[str, Any]) -> int:
        created_at = DotSeparatedPathUtil.get(data, self._created_at_name)
        if not self._is_created_at_value_valid(created_at):
            raise InvalidInputException(
                f"The mandatory {self._created_at_name} field has missing "
                "or has invalid type values in the input object."
            )
        return cast(int, created_at)

    async def _parse_schema_field_values(
        self, field: SchemaField[SFT], datas: Sequence[dict[str, Any]]
    ) -> Sequence[SFT | None]:
        path: str = self._get_path(field)
        parsed_values = [DotSeparatedPathUtil.get(data, path) for data in datas]

        if isinstance(field, SchemaReference):
            return [cast(SFT, str(parsed_value)) if parsed_value else None for parsed_value in parsed_values]

        if isinstance(field, Blob):
            return cast(Sequence[SFT], await self.blob_loader.load(parsed_values))

        return parsed_values

    def __get_all_fields_from_parsed_schema(self, parsed_schema: ParsedSchema) -> list[ParsedSchemaField]:
        return (
            list(parsed_schema.fields)
            + [ParsedSchemaField.from_schema_field(self._schema.id, parsed_schema.id_)]
            + (
                [
                    ParsedSchemaField.from_schema_field(
                        cast(EventSchemaObject, self._schema).created_at,
                        cast(EventParsedSchema, parsed_schema).created_at,
                    )
                ]
                if self._is_event_data_parser
                else []
            )
        )
