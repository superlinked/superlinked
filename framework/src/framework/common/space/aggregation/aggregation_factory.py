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


from beartype.typing import Mapping

from superlinked.framework.common.exception import NotImplementedException
from superlinked.framework.common.space.aggregation.aggregation import (
    Aggregation,
    AvgAggregation,
    MaxAggregation,
    MinAggregation,
    VectorAggregation,
)
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationConfig,
    AggregationInputT,
    AvgAggregationConfig,
    MaxAggregationConfig,
    MinAggregationConfig,
    VectorAggregationConfig,
)

AGGREGATION_BY_CONFIG_CLASS: Mapping[type[AggregationConfig], type[Aggregation]] = {
    VectorAggregationConfig: VectorAggregation,
    AvgAggregationConfig: AvgAggregation,
    MinAggregationConfig: MinAggregation,
    MaxAggregationConfig: MaxAggregation,
}


class AggregationFactory:
    @staticmethod
    def create_aggregation(
        aggregation_config: AggregationConfig[AggregationInputT],
    ) -> Aggregation[AggregationInputT]:
        if aggregation_class := AGGREGATION_BY_CONFIG_CLASS.get(type(aggregation_config)):
            return aggregation_class(aggregation_config)
        raise NotImplementedException(
            "Unknown aggregation config type.", aggregation_config_type=type(aggregation_config).__name__
        )
