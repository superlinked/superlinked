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

import datetime

import altair as alt
import numpy as np
import pandas as pd
from beartype.typing import Mapping, cast

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.calculation.vector_similarity import (
    VectorSimilarityCalculator,
)
from superlinked.framework.common.dag.context import (
    ContextValue,
    ExecutionContext,
    ExecutionEnvironment,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.recency_embedding_config import (
    RecencyEmbeddingConfig,
)
from superlinked.framework.common.space.embedding.model_based.singleton_embedding_engine_manager import (
    SingletonEmbeddingEngineManager,
)
from superlinked.framework.common.transform.transformation_factory import (
    TransformationFactory,
)
from superlinked.framework.common.util.async_util import AsyncUtil
from superlinked.framework.dsl.space.recency_space import RecencySpace


class RecencyPlotter:
    """
    A helper class used to plot recency scores.
    """

    def __init__(
        self,
        recency_space: RecencySpace,
        vector_similarity_calculator: VectorSimilarityCalculator = VectorSimilarityCalculator(
            DistanceMetric.INNER_PRODUCT
        ),
        negative_filter_time_period_showcase_multiplier: float = 1.1,
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
    ) -> None:
        """
        Sets up the RecencyPlotter object. Provide it with a space, and observe the score
        of time points calculated back from `now`.

        Args:
            recency_space (RecencySpace): An instance of RecencySpace class.
            negative_filter_time_period_showcase_multiplier (float): A multiplier to adjust
            the time frame for showcasing negative filter area.
                1.1 means 10% of the largest period time is additionally presented in the
                chart. Default value tends to work nicely.
        """
        self.context: ExecutionContext = ExecutionContext.from_context_data(
            context_data, environment=ExecutionEnvironment.IN_MEMORY
        )
        self._embedding_config = cast(RecencyEmbeddingConfig, recency_space.transformation_config.embedding_config)
        self._embedding_transformation = TransformationFactory.create_embedding_transformation(
            recency_space.transformation_config, SingletonEmbeddingEngineManager()
        )
        self._negative_filter_time_period_showcase_multiplier = negative_filter_time_period_showcase_multiplier
        self.vector_similarity_calculator = vector_similarity_calculator

    def plot_recency_curve(
        self,
        num_points: int = 1000,
        width: int = 500,
        height: int = 380,
        chart_point_size: int = 10,
    ) -> alt.Chart:
        """
        Returns a Chart object with plotted recency scores of time points calculated back from `now`.

        Args:
            num_points (int, optional): The number of points to plot. Defaults to 1000.
            width (int, optional): The width of the chart. Defaults to 500.
            height (int, optional): The height of the chart. Defaults to 380.
            chart_point_size (int, optional): The size of the points on the chart. Defaults to 10.

        Returns:
            alt.Chart: A Chart object with plotted recency scores.
        """
        now_ts: int = self.context.now()
        max_period_time_ts: int = int(
            max(period_time.period_time for period_time in self._embedding_config.period_time_list).total_seconds()
        )

        oldest_ts_to_plot: int = int(
            now_ts - (max_period_time_ts * self._negative_filter_time_period_showcase_multiplier)
        )

        df: pd.DataFrame = self._generate_recency_scores(oldest_ts_to_plot, now_ts, num_points)

        return (
            alt.Chart(df)
            .mark_point(size=chart_point_size, color="black", filled=True)
            .encode(
                x=alt.X("date", title="Date"),
                y=alt.Y("score", title="Recency score"),
                tooltip=["date"],
            )
            .properties(width=width, height=height, title="Recency scores (unit weight)")
        )

    def _generate_recency_scores(self, oldest_ts_to_plot: int, now_ts: int, num_points: int) -> pd.DataFrame:
        plot_timestamps: np.ndarray = np.linspace(start=oldest_ts_to_plot, stop=now_ts, num=num_points)
        recency_vectors: list[Vector] = [
            AsyncUtil.run(self._embedding_transformation.transform(plot_ts, self.context))
            for plot_ts in plot_timestamps
        ]
        now_vector: Vector = AsyncUtil.run(
            self._embedding_transformation.transform(
                now_ts,
                ExecutionContext.from_context_data(self.context.data, environment=ExecutionEnvironment.QUERY),
            )
        )
        recency_scores: list[float] = [
            self.vector_similarity_calculator.calculate_similarity(now_vector, vec) for vec in recency_vectors
        ]
        date_labels: list[datetime.datetime] = [datetime.datetime.fromtimestamp(ts) for ts in plot_timestamps]
        return pd.DataFrame({"date": date_labels, "score": recency_scores})
