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

from beartype.typing import Any, Mapping, Sequence
from pandas import DataFrame

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)


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
    """

    schema: IdSchemaObject
    entries: Sequence[ResultEntry]
    knn_params: Mapping[str, Any] | None = None

    def to_pandas(self) -> DataFrame:
        """
        Converts the query result entries into a pandas DataFrame.

        Each row in the DataFrame corresponds to a single entity in the result, with
        columns representing the fields of the stored objects.

        Returns:
            DataFrame: A pandas DataFrame where each row represents a result entity, and
                each column corresponds to the fields of the stored objects.
        """
        return DataFrame([entry.stored_object for entry in self.entries])

    def __str__(self) -> str:
        return "\n".join(
            f"#{i+1} id:{entry.entity.header.object_id}, object:{entry.stored_object}"
            for i, entry in enumerate(self.entries)
        )
