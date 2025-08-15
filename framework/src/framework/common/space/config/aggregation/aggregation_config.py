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

from abc import ABC
from dataclasses import dataclass

from beartype.typing import Any, Generic, TypeVar

from superlinked.framework.common.data_types import Vector

AggregationInputT = TypeVar("AggregationInputT")


@dataclass(frozen=True)
class AggregationConfig(ABC, Generic[AggregationInputT]):
    aggregation_input_type: type[AggregationInputT]

    def _get_aggregation_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__, "aggregation_input_type": self.aggregation_input_type.__name__}


NumberAggregationInputT = TypeVar("NumberAggregationInputT", float, int)


@dataclass(frozen=True)
class VectorAggregationConfig(AggregationConfig[Vector]):
    pass


@dataclass(frozen=True)
class AvgAggregationConfig(Generic[NumberAggregationInputT], AggregationConfig[NumberAggregationInputT]):
    pass


@dataclass(frozen=True)
class MinAggregationConfig(Generic[NumberAggregationInputT], AggregationConfig[NumberAggregationInputT]):
    pass


@dataclass(frozen=True)
class MaxAggregationConfig(Generic[NumberAggregationInputT], AggregationConfig[NumberAggregationInputT]):
    pass
