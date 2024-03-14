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
from typing import Any, Generic

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
from superlinked.framework.common.schema.id_schema_object import (
    IdSchemaObjectT,
    SchemaField,
)


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

    def _get_column_name_to_schema_field_mapping(self) -> dict[str, SchemaField]:
        reverse_mapping: dict[str, SchemaField] = {
            self.mapping.get(field, field.name) if self.mapping else field.name: field
            for field in self._schema._get_schema_fields() + [self._schema.id]
        }
        return reverse_mapping

    def unmarshal(self, data: pd.DataFrame) -> list[ParsedSchema]:
        """
        Parses the given DataFrame into a list of ParsedSchema objects according to the defined schema and mapping.

        Args:
            data (pd.DataFrame): Pandas DataFrame input.

        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.
        """
        schema_cols: dict[str, SchemaField] = (
            self._get_column_name_to_schema_field_mapping()
        )

        self._ensure_id(data)

        records: list[dict[str, Any]] = data.loc[:, list(schema_cols.keys())].to_dict(
            orient="records"
        )
        return [
            ParsedSchema(
                self._schema,
                record[self._id_name],
                [
                    ParsedSchemaField.from_schema_field(
                        schema_field=schema_cols[key], value=value
                    )
                    for key, value in record.items()
                    if key != self._id_name and not pd.isnull(value)
                ],
            )
            for record in records
        ]

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
        return [pd.DataFrame(records)]

    def _ensure_id(self, data: pd.DataFrame) -> None:
        if self._id_name not in data.columns:
            raise KeyError(
                f"No {self._id_name} column in supplied dataframe. Create a unique id column with the specified name."
            )
        ids: pd.Series = data[self._id_name]
        if any(not self._is_id_value_valid(id_val) for id_val in ids.tolist()):
            raise MissingIdException(
                "The mandatory id field has missing values in the input object."
            )
        vc_ids = ids.value_counts()
        if vc_ids.max() > 1:
            duplicate_ids = vc_ids[vc_ids > 1].index.tolist()
            raise DuplicateIdException(
                f"Multiple rows have the same id: {', '.join([str(f) for f in duplicate_ids])}"
            )
