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

from collections.abc import Mapping
from typing import Generic

import pandas as pd

from superlinked.framework.common.parser.data_parser import DataParser
from superlinked.framework.common.parser.exception import (
    DuplicateIdException,
    MissingIdException,
)
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.event_schema_object import SchemaReference
from superlinked.framework.common.schema.id_schema_object import (
    IdSchemaObjectT,
    SchemaField,
)
from superlinked.framework.common.schema.schema_object import Timestamp


class DataFrameParser(
    Generic[IdSchemaObjectT], DataParser[IdSchemaObjectT, pd.DataFrame]
):
    """
    DataFrameParser gets a `pd.DataFrame` and using column-string mapping
    it transforms the `DataFrame` to a desired schema.
    """

    def __init__(
        self, schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str] | None = None
    ) -> None:
        super().__init__(schema, mapping)
        self._id_name = self.mapping.get(self._schema.id, self._schema.id.name)

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

        if timestamp_cols := [
            key for key, value in schema_cols.items() if isinstance(value, Timestamp)
        ]:
            data_copy[timestamp_cols] = data_copy[timestamp_cols].astype(int)

        data_copy[self._id_name] = data_copy[self._id_name].astype(str)
        schema_ref_cols = [
            key
            for key, value in schema_cols.items()
            if isinstance(value, SchemaReference)
        ]
        data_copy[schema_ref_cols] = data_copy[schema_ref_cols].astype(str)

        records = data_copy[list(schema_cols.keys())].to_dict(orient="records")

        parsed_schemas = [
            ParsedSchema(
                self._schema,
                record[self._id_name],
                [
                    ParsedSchemaField.from_schema_field(
                        schema_field=schema_cols[key], value=value
                    )
                    for key, value in record.items()
                    if key != self._id_name
                    and (
                        bool(value) if isinstance(value, list) else not pd.isnull(value)
                    )
                ],
            )
            for record in records
        ]

        return parsed_schemas

    def _marshal(
        self,
        parsed_schemas: list[ParsedSchema],
    ) -> list[pd.DataFrame]:
        """
        Converts a list of ParsedSchema objects into a list of pandas DataFrame.
        You can use this functionality to check, if your mapping was defined properly.
        Args:
            parsed_schemas (list[ParsedSchema]): A list of ParsedSchema objects that you get
                after unmarshaling your `DataFrame`.
        Returns:
            list[pd.DataFrame]: A list of DataFrame representation of the parsed schemas.
        """
        records = [
            {
                **{self._id_name: parsed_schema.id_},
                **{
                    field.schema_field.name: field.value
                    for field in parsed_schema.fields
                },
            }
            for parsed_schema in parsed_schemas
        ]
        return [pd.DataFrame.from_records(records)]  # type: ignore[attr-defined]

    def _get_column_name_to_schema_field_mapping(self) -> dict[str, SchemaField]:
        return {
            self.mapping.get(field, field.name): field
            for field in list(self._schema._get_schema_fields()) + [self._schema.id]
        }

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

    def _has_missing_ids(self, data: pd.DataFrame) -> bool:
        return any(
            not self._is_id_value_valid(id_val)
            for id_val in data[self._id_name].tolist()
        )

    def _find_duplicate_ids(self, data: pd.DataFrame) -> list[str]:
        mask = data[self._id_name]
        duplicate_mask = mask.duplicated()
        return mask[duplicate_mask].unique().tolist()
