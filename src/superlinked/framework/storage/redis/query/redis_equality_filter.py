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

from superlinked.framework.common.storage.query.equality_filter import EqualityFilter


@dataclass(frozen=True)
class RedisEqualityFilter(EqualityFilter):
    def __get_param_prefix(self) -> str:
        return "not_" if self.negated else ""

    def __get_query_prefix(self) -> str:
        return "-" if self.negated else ""

    def __get_param_name(self) -> str:
        return f"{self.__get_param_prefix()}{self.field_name}_param"

    def get_prefix(self) -> str:
        return (
            f"{self.__get_query_prefix()}@{self.field_name}:${self.__get_param_name()}"
        )

    def get_params(self) -> set[tuple[str, str]]:
        return set([(self.__get_param_name(), self.field_value)])
