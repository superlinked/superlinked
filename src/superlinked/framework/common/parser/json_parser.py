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

from typing import Generic, cast

from superlinked.framework.common.data_types import Json
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.exception import MissingIdException
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObjectT
from superlinked.framework.common.schema.schema_object import SFT, SchemaField
from superlinked.framework.common.util.dot_separated_path_util import (
    DotSeparatedPathUtil,
    ValuedDotSeparatedPath,
)


class JsonParser(Generic[IdSchemaObjectT], DataParser[IdSchemaObjectT, Json]):
    """
    JsonParser gets a `Json` object and using `str` based dot separated path mapping
    it transforms the `Json` to a desired schema.
    """

    def unmarshal(self, data: Json) -> list[ParsedSchema]:
        """
        Parses the given Json into a list of ParsedSchema objects according to the defined schema and mapping.

        Args:
            data (Json): The Json representation of your data.

        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.
        """

        id_ = self.__ensure_id(data)
        parsed_fields: list[ParsedSchemaField] = [
            ParsedSchemaField.from_schema_field(field, parsed_value)
            for field, parsed_value in [
                (field, self._parse_schema_field_value(field, data))
                for field in self._schema._get_schema_fields()
            ]
            if parsed_value is not None
        ]
        return [ParsedSchema(self._schema, id_, parsed_fields)]

    def _marshal(
        self,
        parsed_schemas: list[ParsedSchema],
    ) -> list[Json]:
        """
        Converts a ParsedSchema objects back into a list of Json objects.
        You can use this functionality to check, if your mapping was defined properly.

        Args:
            parsed_schemas (list[ParsedSchema]): ParserSchema in a list that you can
                retrieve after unmarshalling your `Json`.

        Returns:
            list[Json]: List of Json representation of the schemas.
        """
        return [
            self.__construct_json(list_of_schema_fields)
            for list_of_schema_fields in [
                self.__get_all_fields_from_parsed_schema(parsed_schema)
                for parsed_schema in parsed_schemas
            ]
        ]

    def __construct_json(self, parsed_schema_field: list[ParsedSchemaField]) -> Json:
        return DotSeparatedPathUtil.to_dict(
            [
                ValuedDotSeparatedPath(
                    self.__get_path(field.schema_field),
                    field.value,
                )
                for field in parsed_schema_field
            ]
        )

    def __ensure_id(self, data: Json) -> str:
        id_ = self._parse_schema_field_value(self._schema.id, data)
        if not self._is_id_value_valid(id_):
            raise MissingIdException(
                "The mandatory id field is missing from the input object."
            )
        return cast(str, id_)

    def _parse_schema_field_value(
        self, field: SchemaField[SFT], data: Json
    ) -> SFT | None:
        path: str = self.__get_path(field)
        return DotSeparatedPathUtil.get(data, path)

    def __get_path(self, field: SchemaField[SFT]) -> str:
        return self.mapping.get(field, field.name)

    def __get_all_fields_from_parsed_schema(
        self, parsed_schema: ParsedSchema
    ) -> list[ParsedSchemaField]:
        return parsed_schema.fields + [
            ParsedSchemaField.from_schema_field(self._schema.id, parsed_schema.id_)
        ]
