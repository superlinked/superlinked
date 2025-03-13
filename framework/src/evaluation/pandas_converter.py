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

import pandas as pd
from beartype.typing import Any
from pandas import DataFrame

from superlinked.framework.dsl.query.result import QueryResult

DEFAULT_SCORE_FIELD_NAME = "similarity_score"
FALLBACK_SCORE_FIELD_NAME = f"superlinked_{DEFAULT_SCORE_FIELD_NAME}"


class PandasConverter:
    """Converts Result objects to pandas DataFrames.

    This class provides functionality to transform Result objects into pandas DataFrames
    while preserving all relevant information including metadata and scores.

    Methods:
        to_pandas: Converts a Result object to a pandas DataFrame
    """

    @staticmethod
    def to_pandas(result: QueryResult) -> DataFrame:
        """
        Converts the query result entries into a pandas DataFrame.
        Each row in the DataFrame corresponds to a single entity in the result, with
        columns representing the fields of the stored objects. An additional score column
        is present which shows similarity to the query vector.

        Returns:
            DataFrame: A pandas DataFrame where each row represents a result entity, and
                each column corresponds to the fields of the stored objects. Additionally,
                it contains the above-mentioned score column.

        Raises:
            ValueError: If both 'similarity_score' and 'superlinked_similarity_score' fields are present.
        """
        dataframe_rows = []
        for entry in result.entries:
            dataframe_row = entry.fields.copy()
            score_field = PandasConverter._determine_field_name(
                dataframe_row, DEFAULT_SCORE_FIELD_NAME, FALLBACK_SCORE_FIELD_NAME
            )
            dataframe_row["id"] = entry.id
            dataframe_row[score_field] = entry.metadata.score
            dataframe_rows.append(dataframe_row)
        return DataFrame(dataframe_rows)

    @staticmethod
    def format_date_column(
        df: DataFrame, original_column_name: str, new_column_name: str | None = None, year_only: bool = False
    ) -> DataFrame:
        """
        Converts a timestamp column to a date column and drops the original.

        Args:
            df (DataFrame): The DataFrame containing the column to be converted.
            original_column_name (str): The name of the column containing the timestamps.
            new_column_name (str): The name of the new column to be created.

        Returns:
            DataFrame: The DataFrame with the new date or year column.
        """
        if new_column_name is None:
            new_column_name = original_column_name
        if year_only:
            df[new_column_name] = pd.to_datetime(  # type: ignore # mypy doesn't recognize to_datetime method
                df[original_column_name], unit="s", utc=True
            ).dt.year
        else:
            df[new_column_name] = pd.to_datetime(  # type: ignore # mypy doesn't recognize to_datetime method
                df[original_column_name], unit="s", utc=True
            ).dt.date
        if new_column_name != original_column_name:
            df.drop(columns=[original_column_name], inplace=True)
        return df

    @staticmethod
    def _determine_field_name(dataframe_row: dict[str, Any], default_field: str, fallback_field: str) -> str:
        if default_field not in dataframe_row:
            return default_field
        if fallback_field not in dataframe_row:
            return fallback_field
        raise ValueError(f"Data must not contain field named {fallback_field}")
