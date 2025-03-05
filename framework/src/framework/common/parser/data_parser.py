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

from abc import ABC, abstractmethod
from math import isfinite

from beartype.typing import Generic, Mapping, Sequence, cast

from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.parser.blob_loader import BlobLoader
from superlinked.framework.common.parser.exception import InvalidMappingException
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.exception import SchemaMismatchException
from superlinked.framework.common.schema.id_schema_object import (
    IdSchemaObject,
    IdSchemaObjectT,
)
from superlinked.framework.common.schema.schema_object import SFT, Blob, SchemaField
from superlinked.framework.common.source.types import SourceTypeT


class DataParser(ABC, Generic[IdSchemaObjectT, SourceTypeT]):
    """
    A DataParser describes the interface to get a source data to the format of a defined schema with mapping support.

    Attributes:
        mapping (Mapping[SchemaField, str], optional): Source to SchemaField mapping rules
            as `SchemaField`-`str` pairs such as `{movie_schema.title: "movie_title"}`.
    """

    def __init__(self, schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str] | None = None) -> None:
        """
        Initialize DataParser

        Get the desired output schema and initialize a default mapping
        that can be extended by DataParser realizations.

        Args:
            schema (IdSchemaObjectT): SchemaObject describing the desired output.
            mapping (Mapping[SchemaField, str], optional): Realizations can use the `SchemaField` to `str` mapping
                to define their custom mapping logic.

        Raises:
            InitializationException: Parameter `schema` is of invalid type.
        """
        if not isinstance(schema, IdSchemaObject):
            raise InitializationException(f"Parameter `schema` is of invalid type: {schema.__class__.__name__}")
        self._is_event_data_parser = isinstance(schema, EventSchemaObject)
        mapping = mapping or {}
        self.__validate_mapping_against_schema(schema, mapping)
        self.mapping = mapping
        self._schema = schema
        self._id_name = self._get_path(self._schema.id)
        if self._is_event_data_parser:
            self._created_at_name = self._get_path(cast(EventSchemaObject, schema).created_at)
        self.__allow_bytes_input = True

    @property
    def blob_loader(self) -> BlobLoader:
        return BlobLoader(allow_bytes=self.allow_bytes_input)

    @property
    def allow_bytes_input(self) -> bool:
        return self.__allow_bytes_input

    def set_allow_bytes_input(self, value: bool) -> None:
        self.__allow_bytes_input = value

    @classmethod
    def _is_id_value_valid(cls, value_to_check: str | float | int | None) -> bool:
        """Function to check if value is not missing (NaN, infinity, None or empty)

        Args:
            value_to_check: id value to validate

        Returns:
            True if the id value is valid
        """

        if value_to_check is None:
            return False

        if not isinstance(value_to_check, (str, int, float)):
            raise TypeError(
                (
                    f"Param value_to_check should be instance of str, int, float, got {value_to_check} ",
                    f"of type {type(value_to_check)}",
                )
            )

        if isinstance(value_to_check, str) and value_to_check.strip() == "":
            return False

        if isinstance(value_to_check, (int, float)) and not isfinite(value_to_check):
            return False

        return True

    @classmethod
    def _is_created_at_value_valid(cls, value_to_check: int | None) -> bool:
        """Function to check if value is
        not missing (NaN, infinity, None or empty)

        Args:
            value_to_check: created at value to validate

        Returns:
            True if the created_at value is valid
        """

        if value_to_check is None:
            return False
        if not isinstance(value_to_check, int):
            raise TypeError(
                (
                    f"Param value_to_check should be instance of int {value_to_check} ",
                    f"of type {type(value_to_check)}",
                )
            )
        return True

    @abstractmethod
    def unmarshal(self, data: SourceTypeT) -> list[ParsedSchema]:
        """
        Get the source data and parse it to the desired Schema with the defined mapping.

        Args:
            data (TSourceType): Source data that corresponds to the DataParser's type.

        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects.
        """

    @abstractmethod
    def _marshal(self, parsed_schemas: list[ParsedSchema]) -> list[SourceTypeT]:
        pass

    def marshal(
        self,
        parsed_schemas: ParsedSchema | list[ParsedSchema],
    ) -> list[SourceTypeT]:
        """
        Get a previously parsed data and return it to it's input format.

        Args:
            parsed_schemas: Previously parsed data that follows the schema of the `DataParser`.

        Returns:
            list[SourceTypeT]: A list of the original source data format after marshalling the parsed data.
        """
        if not isinstance(parsed_schemas, list):
            parsed_schemas = [parsed_schemas]
        self.__check_parsed_schemas(parsed_schemas)
        return self._marshal(parsed_schemas)

    def _get_path(self, field: SchemaField[SFT]) -> str:
        return self.mapping.get(field, field.name)

    def __validate_mapping_against_schema(self, schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str]) -> None:
        schema_fields = list(schema.schema_fields) + [schema.id]
        if self._is_event_data_parser:
            schema_fields.append(cast(EventSchemaObject, schema).created_at)
        if invalid_keys := [key for key in mapping.keys() if key not in schema_fields]:
            invalid_key_names = [f"{key.schema_obj._base_class_name}.{key.name}" for key in invalid_keys]
            raise InvalidMappingException(f"{invalid_key_names} don't belong to the {schema._base_class_name} schema.")

    def _handle_parsed_schema_fields(
        self, parsed_schema_fields: Sequence[ParsedSchemaField]
    ) -> list[ParsedSchemaField]:
        return [DataParser._re_parse_if_blob(parsed_field) for parsed_field in parsed_schema_fields]

    @staticmethod
    def _re_parse_if_blob(parsed_field: ParsedSchemaField) -> ParsedSchemaField:
        if isinstance(parsed_field.schema_field, Blob):
            parsed_field = cast(ParsedSchemaField[BlobInformation], parsed_field)
            parsed_field = ParsedSchemaField(parsed_field.schema_field, parsed_field.value.original)
        return parsed_field

    def __check_parsed_schemas(self, parsed_schemas: list[ParsedSchema]) -> None:
        if not_valid_schema_base_class_names := [
            parsed_schema.schema._base_class_name
            for parsed_schema in parsed_schemas
            if parsed_schema.schema != self._schema
        ]:
            raise SchemaMismatchException(
                (
                    f"{self.__class__.__name__} can only marshal {self._schema._base_class_name}, ",
                    f"got {not_valid_schema_base_class_names}",
                )
            )
