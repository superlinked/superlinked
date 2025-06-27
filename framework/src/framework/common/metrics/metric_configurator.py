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

from superlinked.framework.common.metrics.metric_registry import (
    MetricRegistry,
    MetricType,
)
from superlinked.framework.common.settings import Settings


class SuperlinkedMetricConfigurator:
    @staticmethod
    def configure_default_metrics() -> None:
        settings = Settings()
        metric_registry = MetricRegistry()

        # Attach labels if the registry instance already exists
        labels = {
            "app_id": settings.APP_ID,
        }
        metric_registry.add_labels(labels)

        metric_registry.create_metric(
            MetricType.COUNTER, "embeddings_total", "Total number of embeddings calculated", "1"
        )
