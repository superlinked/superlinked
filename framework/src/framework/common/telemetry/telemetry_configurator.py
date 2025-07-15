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

from superlinked.framework.common.settings import settings
from superlinked.framework.common.telemetry.telemetry_registry import (
    MetricType,
    telemetry,
)
from superlinked.framework.common.util.version_resolver import VersionResolver


class SuperlinkedTelemetryConfigurator:
    @staticmethod
    def configure_default_metrics() -> None:

        telemetry.add_labels(
            {
                "app_id": settings.APP_ID,
                "superlinked_version": VersionResolver.get_version_for_package("superlinked") or "unknown",
            }
        )

        telemetry.create_metric(MetricType.COUNTER, "engine.embed.count", "Total number of embeddings calculated", "1")
        telemetry.create_metric(
            MetricType.COUNTER, "vdb.write.count", "Total number of embeddings written to the vector database", "1"
        )
        telemetry.create_metric(
            MetricType.COUNTER, "vdb.read.count", "Total number of embeddings read from the vector database", "1"
        )
        telemetry.create_metric(
            MetricType.COUNTER, "vdb.knn.count", "Total number of KNN queries executed on the vector database", "1"
        )
