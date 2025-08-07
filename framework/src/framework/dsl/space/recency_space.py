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

import math
from datetime import timedelta

import structlog
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.dag.recency_node import RecencyNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import Timestamp
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationConfig,
    AvgAggregationConfig,
    MaxAggregationConfig,
    MinAggregationConfig,
)
from superlinked.framework.common.space.config.embedding.recency_embedding_config import (
    RecencyEmbeddingConfig,
)
from superlinked.framework.common.space.config.normalization.normalization_config import (
    ConstantNormConfig,
)
from superlinked.framework.common.space.config.transformation_config import (
    TransformationConfig,
)
from superlinked.framework.dsl.space.has_space_field_set import HasSpaceFieldSet
from superlinked.framework.dsl.space.input_aggregation_mode import InputAggregationMode
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

logger = structlog.getLogger()

DEFAULT_PERIOD_TIME = PeriodTime(period_time=timedelta(days=14))


class RecencySpace(Space[int, int], HasSpaceFieldSet):  # pylint: disable=too-many-instance-attributes
    """
    Recency space encodes timestamp type data measured in seconds and in unix timestamp format.
    Recency space is utilized to encode how recent items are. Use period_time_list
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
        timestamp: Timestamp | None | Sequence[Timestamp | None],
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
            aggregation_mode (InputAggregationMode): The  aggregation mode of the recency embedding.
                Possible values are: maximum, minimum and average. Defaults to InputAggregationMode.INPUT_AVERAGE.
            negative_filter (float): The recency score of items that are older than the oldest period time.
                Defaults to 0.0.
        """
        non_none_timestamp = self._fields_to_non_none_sequence(timestamp)
        super().__init__(non_none_timestamp, Timestamp)
        self._aggregation_config_type_by_mode = self.__init_aggregation_config_type_by_mode()
        self.timestamp = SpaceFieldSet[int](self, set(non_none_timestamp))
        recency_periods: list[PeriodTime] = (
            period_time_list
            if isinstance(period_time_list, list)
            else ([period_time_list] if period_time_list is not None else [DEFAULT_PERIOD_TIME])
        )
        self._aggregation_mode: InputAggregationMode = aggregation_mode
        self._embedding_config = RecencyEmbeddingConfig(
            int,
            recency_periods,
            time_period_hour_offset,
            negative_filter,
        )
        self._transformation_config = self._init_transformation_config(
            self._embedding_config, self._aggregation_mode, recency_periods
        )
        self._schema_node_map: dict[IdSchemaObject, EmbeddingNode[int, int]] = {
            field.schema_obj: RecencyNode(
                parent=SchemaFieldNode(field),
                transformation_config=self._transformation_config,
                fields_for_identification=self.timestamp.fields,
            )
            for field in self.timestamp.fields
        }
        self._max_period_time_days = (
            max(self._embedding_config.period_time_list, key=lambda p: p.period_time).period_time.total_seconds()
            / 86400
        )

    @property
    @override
    def space_field_set(self) -> SpaceFieldSet:
        return self.timestamp

    @property
    @override
    def transformation_config(self) -> TransformationConfig[int, int]:
        return self._transformation_config

    def __init_aggregation_config_type_by_mode(
        self,
    ) -> dict[InputAggregationMode, type[AggregationConfig]]:
        return {
            InputAggregationMode.INPUT_AVERAGE: AvgAggregationConfig,
            InputAggregationMode.INPUT_MINIMUM: MinAggregationConfig,
            InputAggregationMode.INPUT_MAXIMUM: MaxAggregationConfig,
        }

    @property
    @override
    def _embedding_node_by_schema(
        self,
    ) -> dict[IdSchemaObject, EmbeddingNode[int, int]]:
        return self._schema_node_map

    @property
    @override
    def _annotation(self) -> str:
        return f"""The space encodes timestamps between now and now - {self._max_period_time_days} days.
        Older timestamps will have negative_filter similarity (assuming weight = 1).
        There is no differentiation between items older than {self._max_period_time_days} days.
        We always query with now, so the similarity contribution of items will always be proportional to their recency.
        Setting weight to 0 desensitizes the results to recency, negative weights favor older items and positive
        weights will favor recent ones.
        Also take into account that max_period_time is {self._max_period_time_days} days".
        Favoring values from {self._max_period_time_days/2} days ago could best be achieved using positive weights
        lower than the other weights in the query.
        Larger positive weights increase the effect on similarity compared to other spaces.
        Does not have input as querying will always happen using the utc timestamp of the system's NOW.
        Affected fields: {self.space_field_set.field_names_text}."""

    @property
    @override
    def _allow_empty_fields(self) -> bool:
        return True

    @property
    @override
    def allow_similar_clause(self) -> bool:
        return False

    def _init_transformation_config(
        self,
        embedding_config: RecencyEmbeddingConfig,
        aggregation_mode: InputAggregationMode,
        recency_periods: Sequence[PeriodTime],
    ) -> TransformationConfig[int, int]:
        aggregation_config = self._aggregation_config_type_by_mode[aggregation_mode](int)
        normalization_config = ConstantNormConfig(
            math.sqrt(sum(period_time.weight**2 for period_time in recency_periods))
        )
        return TransformationConfig(
            normalization_config,
            aggregation_config,
            embedding_config,
        )

    @override
    def _create_default_node(self, schema: IdSchemaObject) -> EmbeddingNode[int, int]:
        return RecencyNode(None, self._transformation_config, self.timestamp.fields, schema)
