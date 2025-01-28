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

from abc import ABC, abstractmethod

from beartype.typing import Any

from superlinked.framework.dsl.query.result import QueryResult


class QueryResultConverter(ABC):
    def convert(self, query_result: QueryResult) -> QueryResult:
        copied_object = query_result.model_copy(deep=True)
        self.__iterate_on_conversibles(copied_object)
        return copied_object

    def __iterate_on_conversibles(self, query_result: QueryResult) -> None:
        for entry in query_result.entries:
            for key, value in entry.fields.items():
                entry.fields[key] = self._convert_value(value)

        for key, value in query_result.metadata.search_params.items():
            query_result.metadata.search_params[key] = self._convert_value(value)

    @abstractmethod
    def _convert_value(self, value: Any) -> Any:
        pass
