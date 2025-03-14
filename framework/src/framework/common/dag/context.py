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

from collections import defaultdict
from enum import Enum, auto

from beartype.typing import Mapping, TypeVar, cast
from typing_extensions import Self, TypeAlias

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import (
    NotImplementedException,
    QueryException,
)
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.util import time_util
from superlinked.framework.common.visualize.ingestion_output_recorder import (
    IngestionOutputRecorder,
)
from superlinked.framework.common.visualize.no_op_output_recorder import (
    NoOpOutputRecorder,
)
from superlinked.framework.common.visualize.output_recorder import OutputRecorder
from superlinked.framework.common.visualize.query_output_recorder import (
    QueryOutputRecorder,
)

ContextValue: TypeAlias = int | float | str | Mapping | list | bool | None
T = TypeVar("T", bound=ContextValue)
CONTEXT_COMMON = "common"
CONTEXT_COMMON_ENVIRONMENT = "environment"
CONTEXT_COMMON_NOW = "now"
LOAD_DEFAULT_NODE_INPUT = "load_default_node_input"
SPACE_WEIGHT_PARAM_NAME = "weight"


class ExecutionEnvironment(Enum):
    IN_MEMORY = auto()
    QUERY = auto()
    BATCH = auto()
    ONLINE = auto()


class NowStrategy(Enum):
    SYSTEM_TIME = auto()
    CONTEXT_TIME = auto()
    CONTEXT_OR_SYSTEM_TIME = auto()


class ExecutionContext:
    def __init__(
        self,
        environment: ExecutionEnvironment,
        now_strategy: NowStrategy = NowStrategy.CONTEXT_OR_SYSTEM_TIME,
        data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ) -> None:
        self.__environment = environment
        self.__now_strategy = now_strategy
        self.__data: dict[str, dict[str, ContextValue]] = defaultdict(dict)
        if data:
            self.update_data(data)
        self.__dag_output_recorder = self.__init_output_recorder()

    def update_data(self, data: Mapping[str, Mapping[str, ContextValue]]) -> Self:
        for key, sub_map in data.items():
            self.__data[key].update(sub_map)
        return self

    def now(self) -> int:
        match self.now_strategy:
            case NowStrategy.CONTEXT_OR_SYSTEM_TIME:
                return (
                    self.__data_now() or time_util.now()
                )  # ingestion uses system time for in_memory executor if it is not overridden
            case NowStrategy.CONTEXT_TIME:
                now = self.__data_now()
                if now is None:
                    raise QueryException(
                        (
                            f"Environment's '{CONTEXT_COMMON}.{CONTEXT_COMMON_NOW}' "
                            + "property should always be initialized for query contexts",
                        )
                    )
                return now
            case NowStrategy.SYSTEM_TIME:
                return time_util.now()
            case _:
                raise NotImplementedException(f"Unknown now strategy: {self.now_strategy}")

    @property
    def environment(self) -> ExecutionEnvironment:
        return self.__environment

    @property
    def now_strategy(self) -> NowStrategy:
        return self.__now_strategy

    @property
    def data(self) -> Mapping[str, Mapping[str, ContextValue]]:
        return self.__data

    @property
    def dag_output_recorder(self) -> OutputRecorder:
        return self.__dag_output_recorder

    def get_node_context_value(self, node_id: str, key: str, _: type[T]) -> T | None:
        value = self.__node_context(node_id).get(key)
        if value is None:
            return None

        return cast(T, value)

    def get_weight_of_node(self, node_id: str) -> float:
        weight_param = self.get_node_context_value(node_id, SPACE_WEIGHT_PARAM_NAME, float)
        return float(weight_param if weight_param is not None else constants.DEFAULT_WEIGHT)

    def set_node_context_value(self, node_id: str, key: str, value: ContextValue | None) -> None:
        self.__node_context(node_id)[key] = value

    def get_common_value(self, key: str, _: type[T]) -> T | None:
        value = self.__common_context().get(key)
        if value is None:
            return None
        return cast(T, value)

    def set_common_value(self, key: str, value: ContextValue | None) -> None:
        self.__common_context()[key] = value

    def __data_now(self) -> int | None:
        now_value = self.__common_context().get(CONTEXT_COMMON_NOW)
        return None if now_value is None else int(cast(int, now_value))

    def __common_context(self) -> dict[str, ContextValue]:
        return self.__data[CONTEXT_COMMON]

    def __node_context(self, node_id: str) -> dict[str, ContextValue]:
        return self.__data[node_id]

    def __init_output_recorder(self) -> OutputRecorder:
        if not Settings().ENABLE_DAG_VISUALIZATION:
            return NoOpOutputRecorder()
        if self.is_query_context:
            return QueryOutputRecorder()
        return IngestionOutputRecorder()

    @property
    def is_query_context(self) -> bool:
        return self.environment == ExecutionEnvironment.QUERY

    @classmethod
    def from_context_data(
        cls,
        context_data: Mapping[str, Mapping[str, ContextValue]] | None,
        environment: ExecutionEnvironment,
        now_strategy: NowStrategy = NowStrategy.CONTEXT_OR_SYSTEM_TIME,
    ) -> ExecutionContext:
        return (
            cls(environment, now_strategy)
            if context_data is None
            else cls(environment, now_strategy).update_data(context_data)
        )
