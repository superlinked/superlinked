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

from dataclasses import dataclass

from beartype.typing import Any, Sequence
from pandas import DataFrame

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor

DEFAULT_SCORE_FIELD_NAME = "similarity_score"
DEFAULT_RANK_FIELD_NAME = "rank"
FALLBACK_SCORE_FIELD_NAME = f"superlinked_{DEFAULT_SCORE_FIELD_NAME}"
FALLBACK_RANK_FIELD_NAME = f"superlinked_{DEFAULT_RANK_FIELD_NAME}"


@dataclass(frozen=True)
class ResultEntry:
    """
    Represents a single entry in a Result, encapsulating the entity and its associated data.

    Attributes:
        entity (SearchResultItem): The entity of the result entry.
            This is an instance of the SearchResultItem class, which represents a unique entity in the system.
            It contains header information such as the entity's ID and schema and the queried fields.
        stored_object (dict[str, Any]): The stored object of the result entry.
            This is essentially the raw data that was input into the system.
    """

    entity: SearchResultItem
    stored_object: dict[str, Any]


@dataclass(frozen=True)
class Result:
    """
    A class representing the result of a query.

    Attributes:
        schema (IdSchemaObject): The schema of the result.
        entries (Sequence[ResultEntry]): A list of result entries.
        query_descriptor (QueryDescriptor): The final form of QueryDescriptor used in the query.
    """

    entries: Sequence[ResultEntry]
    query_descriptor: QueryDescriptor

    @property
    def schema(self) -> IdSchemaObject:
        return self.query_descriptor.schema

    @property
    def entities(self) -> list[SearchResultItem]:
        return [entry.entity for entry in self.entries]

    @property
    def knn_params(self) -> dict[str, Any]:
        return self.query_descriptor.calculate_value_by_param_name()

    def to_pandas(self) -> DataFrame:
        """
        Converts the query result entries into a pandas DataFrame.

        Each row in the DataFrame corresponds to a single entity in the result, with
        columns representing the fields of the stored objects. An additional score column
        is present which shows similarity to the query vector.

        Returns:
            DataFrame: A pandas DataFrame where each row represents a result entity, and
                each column corresponds to the fields of the stored objects. Additionally,
                it contains the above-mentioned score column.
            ValueError: If both 'similarity_score' and 'superlinked_similarity_score' fields are present.
        """
        dataframe_rows = [
            self._create_dataframe_row(i, entry) for i, entry in enumerate(self.entries)
        ]
        return DataFrame(dataframe_rows)

    def _create_dataframe_row(self, index: int, entry: ResultEntry) -> dict[str, Any]:
        dataframe_row = entry.stored_object.copy()
        score_field = self._determine_field_name(
            dataframe_row, DEFAULT_SCORE_FIELD_NAME, FALLBACK_SCORE_FIELD_NAME
        )
        rank_field = self._determine_field_name(
            dataframe_row, DEFAULT_RANK_FIELD_NAME, FALLBACK_RANK_FIELD_NAME
        )
        dataframe_row[score_field] = entry.entity.score
        dataframe_row[rank_field] = index
        return dataframe_row

    def _determine_field_name(
        self, dataframe_row: dict[str, Any], default_field: str, fallback_field: str
    ) -> str:
        if default_field not in dataframe_row:
            return default_field
        if fallback_field not in dataframe_row:
            return fallback_field
        raise ValueError(f"Data must not contain field named {fallback_field}")

    def __str__(self) -> str:
        return "\n".join(
            f"#{i+1} id:{entry.entity.header.object_id}, object:{entry.stored_object}"
            for i, entry in enumerate(self.entries)
        )
