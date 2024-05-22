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

import logging
from datetime import timedelta
from typing import Mapping

from typing_extensions import override

from superlinked.framework.common.dag.named_function_node import NamedFunctionNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.dag.recency_node import RecencyNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.schema_object import SchemaObject, Timestamp
from superlinked.framework.common.space.aggregation import InputAggregationMode
from superlinked.framework.common.util.named_function_evaluator import NamedFunction
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

logger = logging.getLogger()

DEFAULT_PERIOD_TIME = PeriodTime(period_time=timedelta(days=14))


class RecencySpace(Space):  # pylint: disable=too-many-instance-attributes
    """
    Recency space encodes timestamp type data measured in seconds and in unix timestamp format.
    Recency space is utilised to encode how recent items are. Use period_time_list
    to mark the time periods of interest.
    Items older than the largest period_time are going to have uniform recency score. (0 or negative_filter if set)
    You can use multiple period_times to give additional emphasis to sub time periods.
    Like using 2 days and 5 days gives extra emphasis to the first 2 days. The extent of which can be controlled with
    the respective weight parameters.
    Unit weights would give double emphasis on the first 2 days, 1 and 0.1 weights respectively
    would give tenfold importance to the first 2 days.
    All items older than 5 days would get 0 or `negative_filter` recency score.
    Negative_filter is useful for effectively filtering out entities that are older than the oldest period time.
    You can think of the value of negative_filter as it offsets that amount of similarity stemming from other
    spaces in the index. For example setting it -1 would offset any text similarity that has weight 1 - effectively
    filtering out all old items however similar they are in terms of their text.

    Attributes:
        timestamp (SpaceFieldSet): A set of Timestamp objects. The actual data is expected to be unix timestamps
            in seconds.
            It is a SchemaFieldObject not regular python ints or floats.
        time_period_hour_offset (timedelta): Starting period time will be set to this hour.
            Day will be the next day of context.now(). Defaults to timedelta(hours=0).
        period_time_list (list[PeriodTime] | None): A list of period time parameters.
            Weights default to 1. Period time to 14 days.
        aggregation_mode (InputAggregationMode): The  aggregation mode of the number embedding.
            Possible values are: maximum, minimum and average. Defaults to InputAggregationMode.INPUT_AVERAGE.
        negative_filter (float): The recency score of items that are older than the oldest period time. Defaults to 0.0.
    """

    def __init__(
        self,
        timestamp: Timestamp | list[Timestamp],
        time_period_hour_offset: timedelta = timedelta(hours=0),
        period_time_list: list[PeriodTime] | PeriodTime | None = None,
        aggregation_mode: InputAggregationMode = InputAggregationMode.INPUT_AVERAGE,
        negative_filter: float = 0.0,
    ) -> None:
        """
        Initialize the RecencySpace.

        Args:
            timestamp (SpaceFieldSet): A set of Timestamp objects. The actual data is expected to be unix timestamps
                in seconds.
                It is a SchemaFieldObject not regular python ints or floats.
            time_period_hour_offset (timedelta): Starting period time will be set to this hour.
                Day will be the next day of context.now(). Defaults to timedelta(hours=0).
            period_time_list (list[PeriodTime] | None): A list of period time parameters.
                Weights default to 1. Period time to 14 days.
            aggregation_mode (InputAggregationMode): The  aggregation mode of the number embedding.
                Possible values are: maximum, minimum and average. Defaults to InputAggregationMode.INPUT_AVERAGE.
            negative_filter (float): The recency score of items that are older than the oldest period time.
                Defaults to 0.0.
        """
        super().__init__(timestamp, Timestamp)
        self.timestamp = SpaceFieldSet(self, self._field_set)
        self.period_time_list: list[PeriodTime] = (
            period_time_list
            if isinstance(period_time_list, list)
            else (
                [period_time_list]
                if period_time_list is not None
                else [DEFAULT_PERIOD_TIME]
            )
        )
        self.negative_filter = negative_filter
        self.time_period_hour_offset = time_period_hour_offset
        self.__aggregation_mode: InputAggregationMode = aggregation_mode
        self.__run_parameter_checks()
        self.__schema_node_map: dict[SchemaObject, RecencyNode] = {
            field.schema_obj: RecencyNode(
                SchemaFieldNode(field),
                self.time_period_hour_offset,
                self.period_time_list,
                self.__aggregation_mode,
                self.negative_filter,
            )
            for field in self.timestamp.fields
        }

    @property
    def _node_by_schema(self) -> Mapping[SchemaObject, Node[Vector]]:
        return self.__schema_node_map

    def __run_parameter_checks(self) -> None:
        if self.negative_filter > 0:
            sum_weights: float = sum(param.weight for param in self.period_time_list)

            max_period_time: timedelta = max(
                param.period_time for param in self.period_time_list
            )
            max_period_time_str = (
                f"{max_period_time.days} days"
                if max_period_time.days
                else f"{round(max_period_time.seconds / 3600, 2)} hours"
            )
            logger.warning(
                "Positive negative_filter value supplied (%s). This will lead to "
                "old items (older than %s) having recency scores of "
                "%s.\nMeanwhile the largest recency score possible for the most "
                "recent items is around %s, and the score at %s will be 0. "
                "\nUse with caution.",
                self.negative_filter,
                max_period_time_str,
                self.negative_filter,
                sum_weights,
                max_period_time_str,
            )

        if any(param.weight < 0 for param in self.period_time_list):
            logger.warning(
                "Negative weight supplied for some period_time_param. This can lead to very strange "
                "recency score curves. Use with caution. \n"
                "To better understand your recency scores use RecencyPlotter."
                "It can be imported from `superlinked.evaluation.charts.recency_plotter`. \n"
                "Check an example notebook at: https://github.com/superlinked/superlinked/blob/main"
                "/notebook/combining_recency_and_relevance.ipynb. "
            )

    @override
    def _handle_node_not_present(self, schema: SchemaObject) -> RecencyNode:
        named_function_node = NamedFunctionNode(NamedFunction.NOW, schema, int)
        recency_node = RecencyNode(
            named_function_node,
            self.time_period_hour_offset,
            self.period_time_list,
            self.__aggregation_mode,
            self.negative_filter,
        )
        self.__schema_node_map[schema] = recency_node
        return recency_node
