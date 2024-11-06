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

import pandas as pd
from beartype.typing import Any, Generic, cast

from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.exception import (
    DuplicateIdException,
    MissingCreatedAtException,
    MissingIdException,
)
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.event_schema_object import (
    EventSchemaObject,
    SchemaReference,
)
from superlinked.framework.common.schema.id_schema_object import (
    IdSchemaObjectT,
    SchemaField,
)
from superlinked.framework.common.schema.schema_object import Blob, String, Timestamp


class DataFrameParser(
    Generic[IdSchemaObjectT], DataParser[IdSchemaObjectT, pd.DataFrame]
):
    """
    DataFrameParser gets a `pd.DataFrame` and using column-string mapping
    it transforms the `DataFrame` to a desired schema.
    """

    def unmarshal(self, data: pd.DataFrame) -> list[ParsedSchema]:
        """
        Parses the given DataFrame into a list of ParsedSchema objects according to the defined schema and mapping.
        Args:
            data (pd.DataFrame): Pandas DataFrame input.
        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.
        """
        data_copy = data.copy()
        schema_cols: dict[str, SchemaField] = (
            self._get_column_name_to_schema_field_mapping()
        )
        self._ensure_id(data_copy)
        if self._is_event_data_parser:
            self.__ensure_created_at(data_copy)

        data_copy[self._id_name] = data_copy[self._id_name].astype(str)
        self._convert_columns_to_type(data_copy, schema_cols, Timestamp)
        self._convert_columns_to_type(data_copy, schema_cols, String)
        self._convert_columns_to_type(data_copy, schema_cols, SchemaReference)

        if blob_cols := [
            key for key, value in schema_cols.items() if isinstance(value, Blob)
        ]:
            data_copy[blob_cols] = data_copy[blob_cols].apply(
                lambda col: col.map(self.blob_loader.load)
            )

        if self._is_event_data_parser:
            data_copy[self._created_at_name] = data_copy[self._created_at_name].astype(
                int
            )
        schema_data = cast(pd.DataFrame, data_copy[list(schema_cols.keys())])
        records = cast(list[dict[str, Any]], schema_data.to_dict(orient="records"))
        return [self.__create_parsed_schema(record, schema_cols) for record in records]

    def __create_parsed_schema(
        self, record: dict[str, Any], schema_cols: dict[str, SchemaField]
    ) -> ParsedSchema:
        admin_field_names = [self._id_name] + (
            [self._created_at_name] if self._is_event_data_parser else []
        )
        other_fields = [
            ParsedSchemaField.from_schema_field(
                schema_field=schema_cols[key], value=value
            )
            for key, value in record.items()
            if key not in admin_field_names and self._field_has_non_null_value(value)
        ]
        id_: str = cast(str, record[self._id_name])
        if self._is_event_data_parser:
            return EventParsedSchema(
                self._schema,
                id_,
                other_fields,
                cast(int, record[self._created_at_name]),
            )
        return ParsedSchema(self._schema, id_, other_fields)

    def _field_has_non_null_value(self, value: Any) -> bool:
        values_to_check = value if isinstance(value, list) else [value]
        return not value or not all(pd.isnull(v) for v in values_to_check)

    def _marshal(
        self,
        parsed_schemas: list[ParsedSchema],
    ) -> list[pd.DataFrame]:
        """
        Converts a list of ParsedSchema objects into a list of pandas DataFrame.
        You can use this functionality to check, if your mapping was defined properly.
        Args:
            parsed_schemas (list[ParsedSchema]): A list of ParsedSchema objects that you get
                after unmarshalling your `DataFrame`.
        Returns:
            list[pd.DataFrame]: A list of DataFrame representation of the parsed schemas.
        """
        records = [
            self.__create_record_dict(parsed_schema) for parsed_schema in parsed_schemas
        ]
        return [pd.DataFrame.from_records(records)]  # type: ignore[attr-defined]

    def __create_record_dict(self, parsed_schema: ParsedSchema) -> dict:
        altered_parsed_schema_fields = self._handle_parsed_schema_fields(
            parsed_schema.fields
        )
        record_dict = {
            **{self._id_name: parsed_schema.id_},
            **{
                field.schema_field.name: field.value
                for field in altered_parsed_schema_fields
            },
        }
        if self._is_event_data_parser:
            if not isinstance(parsed_schema, EventParsedSchema):
                raise MissingCreatedAtException(
                    "Invalid parsed schema, type must be EventParsedSchema"
                )
            record_dict.update({self._created_at_name: parsed_schema.created_at})
        return record_dict

    def _get_column_name_to_schema_field_mapping(self) -> dict[str, SchemaField]:
        schema_fields = list(self._schema._get_schema_fields()) + [self._schema.id]
        if self._is_event_data_parser:
            schema_fields.append(cast(EventSchemaObject, self._schema).created_at)
        return {self._get_path(field): field for field in schema_fields}

    def _ensure_id(self, data: pd.DataFrame) -> None:
        if self._id_name not in data.columns:
            raise KeyError(
                f"No {self._id_name} column in supplied dataframe. Create a unique id column with the specified name."
            )

        if self._has_missing_ids(data):
            raise MissingIdException(
                "The mandatory id field has missing values in the input object."
            )

        if duplicate_ids := self._find_duplicate_ids(data):
            raise DuplicateIdException(
                f"Multiple rows have the same id: {', '.join([str(f) for f in duplicate_ids])}"
            )

    def __ensure_created_at(self, data: pd.DataFrame) -> None:
        if self._created_at_name not in data.columns:
            raise KeyError(
                f"No {self._created_at_name} column in supplied in event dataframe. "
                f"Create a created_at column with the specified name."
            )
        if any(
            not self._is_created_at_value_valid(_created_at_val)
            for _created_at_val in data[self._created_at_name].tolist()
        ):
            raise MissingCreatedAtException(
                "The mandatory created_at field has missing values in the event input object."
            )

    def _has_missing_ids(self, data: pd.DataFrame) -> bool:
        return any(
            not self._is_id_value_valid(id_val)
            for id_val in data[self._id_name].tolist()
        )

    def _find_duplicate_ids(self, data: pd.DataFrame) -> list[str]:
        mask = data[self._id_name]
        duplicate_mask = mask.duplicated()
        return list(mask[duplicate_mask].unique())

    def _convert_columns_to_type(
        self,
        data: pd.DataFrame,
        schema_cols: dict[str, SchemaField],
        schema_field_type: type[SchemaField],
    ) -> None:
        for column_name, schema_field in schema_cols.items():
            if isinstance(schema_field, schema_field_type):
                data[column_name] = data[column_name].astype(schema_field.type_)
