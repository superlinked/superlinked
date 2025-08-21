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

import numpy as np
import pandas as pd
from beartype.typing import Any, Sequence, cast

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.parsed_schema import (
    EventParsedSchema,
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.schema_object import Blob, SchemaField


class DataFrameParser(DataParser[pd.DataFrame]):
    """
    DataFrameParser gets a `pd.DataFrame` and using column-string mapping
    it transforms the `DataFrame` to a desired schema.
    """

    async def unmarshal(self, data: pd.DataFrame) -> list[ParsedSchema]:
        """
        Parses the given DataFrame into a list of ParsedSchema objects according to the defined schema and mapping.
        Args:
            data (pd.DataFrame): Pandas DataFrame input.
        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.
        """
        data_copy = data.copy()
        schema_cols: dict[str, SchemaField] = self._get_column_name_to_schema_field_mapping()
        self._ensure_id(data_copy)

        data_copy[self._id_name] = data_copy[self._id_name].astype(str)
        self._convert_columns_to_type(data_copy, schema_cols)

        if blob_cols := [key for key, value in schema_cols.items() if isinstance(value, Blob)]:
            for col in blob_cols:
                data_copy[col] = await self.blob_loader.load(list(data_copy[col]))

        if self._is_event_data_parser:
            self.__ensure_created_at(data_copy)
            data_copy[self._created_at_name] = data_copy[self._created_at_name].astype(int)
            self.__ensure_created_at_type(data_copy)

        filtered_cols = {col: schema_field for col, schema_field in schema_cols.items() if col in data_copy.columns}
        schema_data = cast(pd.DataFrame, data_copy[list(filtered_cols.keys())])
        records = cast(list[dict[str, Any]], schema_data.to_dict(orient="records"))
        return [self.__create_parsed_schema(record, schema_cols) for record in records]

    def __create_parsed_schema(self, record: dict[str, Any], schema_cols: dict[str, SchemaField]) -> ParsedSchema:
        admin_field_names = [self._id_name] + ([self._created_at_name] if self._is_event_data_parser else [])
        other_fields = [
            ParsedSchemaField.from_schema_field(schema_field=schema_cols[key], value=value)
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

    @staticmethod
    def _check_value_is_null(value: Any) -> bool:
        return value is not None and not pd.isnull(value)

    def _field_has_non_null_value(self, value: Any) -> bool:
        if isinstance(value, (list, np.ndarray)):
            return len(value) == 0 or any(self._check_value_is_null(v) for v in value)
        return self._check_value_is_null(value)

    def _marshal(self, parsed_schemas: Sequence[ParsedSchema]) -> list[pd.DataFrame]:
        records = [self.__create_record_dict(parsed_schema) for parsed_schema in parsed_schemas]
        return [pd.DataFrame.from_records(records)]  # type: ignore[attr-defined]

    def __create_record_dict(self, parsed_schema: ParsedSchema) -> dict:
        altered_parsed_schema_fields = self._handle_parsed_schema_fields(parsed_schema.fields)
        record_dict = {
            **{self._id_name: parsed_schema.id_},
            **{field.schema_field.name: field.value for field in altered_parsed_schema_fields},
        }
        if self._is_event_data_parser:
            if not isinstance(parsed_schema, EventParsedSchema):
                raise InvalidInputException(f"Invalid parsed schema, type must be {EventParsedSchema.__name__}")
            record_dict.update({self._created_at_name: parsed_schema.created_at})
        return record_dict

    def _get_column_name_to_schema_field_mapping(self) -> dict[str, SchemaField]:
        schema_fields = list(self._schema.schema_fields) + [self._schema.id]
        if self._is_event_data_parser:
            schema_fields.append(cast(EventSchemaObject, self._schema).created_at)
        return {self._get_path(field): field for field in schema_fields}

    def _ensure_id(self, data: pd.DataFrame) -> None:
        if self._id_name not in data.columns:
            raise InvalidInputException(
                f"No {self._id_name} column in supplied dataframe. Create a unique id column with the specified name."
            )

        if self._has_missing_ids(data):
            raise InvalidInputException(
                "The mandatory id field has missing or has invalid type values in the input object."
            )

        if duplicate_ids := self._find_duplicate_ids(data):
            raise InvalidInputException(f"Multiple rows have the same id: {', '.join([str(f) for f in duplicate_ids])}")

    def __ensure_created_at(self, data: pd.DataFrame) -> None:
        if self._created_at_name not in data.columns:
            raise InvalidInputException(
                f"No {self._created_at_name} column in supplied in event dataframe. "
                f"Create a created_at column with the specified name."
            )

    def __ensure_created_at_type(self, data: pd.DataFrame) -> None:
        if any(
            not self._is_created_at_value_valid(_created_at_val)
            for _created_at_val in data[self._created_at_name].tolist()
        ):
            raise InvalidInputException("The mandatory created_at field has missing values in the event input object.")

    def _has_missing_ids(self, data: pd.DataFrame) -> bool:
        return any(not self._is_id_value_valid(id_val) for id_val in data[self._id_name].tolist())

    def _find_duplicate_ids(self, data: pd.DataFrame) -> list[str]:
        mask = data[self._id_name]
        duplicate_mask = mask.duplicated()
        return list(mask[duplicate_mask].unique())

    def _convert_columns_to_type(
        self,
        data: pd.DataFrame,
        schema_cols: dict[str, SchemaField],
    ) -> None:
        for column_name, schema_field in schema_cols.items():
            if column_name not in data.columns and schema_field.nullable:
                continue
            # pylint: disable=W0640
            data[column_name] = data[column_name].apply(
                lambda x: schema_field.as_type(x) if self._field_has_non_null_value(x) else None
            )
