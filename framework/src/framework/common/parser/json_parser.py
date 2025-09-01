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

from itertools import accumulate

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
from superlinked.framework.common.schema.schema_object import Blob, SchemaField
from superlinked.framework.common.util.dot_separated_path_util import (
    DotSeparatedPathUtil,
    ValuedDotSeparatedPath,
)


class JsonParser(DataParser[dict[str, Any]]):
    """
    JsonParser gets a `Json` object and using `str` based dot separated path mapping
    it transforms the `Json` to a desired schema.
    """

    async def unmarshal(self, data: Sequence[dict[str, Any]]) -> list[ParsedSchema]:
        """
        Parses the given Json into a list of ParsedSchema objects according to the defined schema and mapping.

        Args:
            data (Json): The Json representation of your data.

        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.
        """
        if isinstance(data, dict):
            data = [data]

        ids = [self.__ensure_id(json_data) for json_data in data]
        all_results = await self._process_fields(self._schema.schema_fields, data)
        parsed_fields_for_each_field = self._create_parsed_fields_for_each_field(all_results)
        parsed_fields_for_each_data = self._transpose_parsed_fields(data, parsed_fields_for_each_field)
        if self._is_event_data_parser:
            created_at_values = [self.__ensure_created_at(json_data) for json_data in data]
            return [
                EventParsedSchema(self._schema, id_, fields, created_at)
                for id_, fields, created_at in zip(ids, parsed_fields_for_each_data, created_at_values)
            ]
        return [ParsedSchema(self._schema, id_, fields) for id_, fields in zip(ids, parsed_fields_for_each_data)]

    async def _process_fields(
        self, fields: Sequence[SchemaField], json_datas: Sequence[dict[str, Any]]
    ) -> list[tuple[SchemaField, list]]:
        if not fields:
            return []
        schema_field_to_values = self._read_field_values(fields, json_datas)
        results: list[tuple[SchemaField, list]] = []
        for field in [field for field in fields if not isinstance(field, Blob)]:
            values = schema_field_to_values[field]
            if isinstance(field, SchemaReference):
                values = [str(value) if value else None for value in values]
            results.append((field, values))
        if blob_fields := [field for field in fields if isinstance(field, Blob)]:
            blob_vals = [value for field in blob_fields for value in schema_field_to_values[field]]
            if blob_vals:
                loaded_blobs = await self._delayed_blob_loader.evaluate(blob_vals)
                lengths = [len(schema_field_to_values[field]) for field in blob_fields]
                offsets = [0, *accumulate(lengths)]
                for f, start, end in zip(blob_fields, offsets, offsets[1:]):
                    results.append((f, loaded_blobs[start:end]))
        return results

    def _read_field_values(
        self, fields: Sequence[SchemaField], json_datas: Sequence[dict[str, Any]]
    ) -> dict[SchemaField, list[Any]]:
        field_paths = {field: self._get_path(field) for field in fields}
        return {field: [DotSeparatedPathUtil.get(data, field_paths[field]) for data in json_datas] for field in fields}

    def _create_parsed_fields_for_each_field(
        self, all_results: Sequence[tuple[SchemaField, Sequence]]
    ) -> list[list[ParsedSchemaField | None]]:
        return [
            [
                ParsedSchemaField.from_schema_field(field, parsed_value) if parsed_value is not None else None
                for parsed_value in parsed_values
            ]
            for field, parsed_values in all_results
        ]

    def _transpose_parsed_fields(
        self,
        json_datas: Sequence[dict[str, Any]],
        parsed_fields_for_each_field: Sequence[Sequence[ParsedSchemaField | None]],
    ) -> list[list[ParsedSchemaField]]:
        result: list[list[ParsedSchemaField]] = [[] for _ in range(len(json_datas))]
        for field_list in parsed_fields_for_each_field:
            for data_idx, field in enumerate(field_list):
                if field is not None:
                    result[data_idx].append(field)
        return result

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
