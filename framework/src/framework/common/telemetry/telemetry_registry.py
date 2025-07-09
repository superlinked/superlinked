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
from contextlib import AbstractContextManager
from enum import Enum

import structlog
from beartype.typing import Any, Type
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import NoOpTracer
from typing_extensions import override

logger = structlog.getLogger(__name__)

DEFAULT_NAME = "superlinked"


class MetricType(Enum):
    COUNTER = "counter"
    HISTOGRAM = "histogram"


class Metric(ABC):
    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "1",
        default_labels: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.metric_type = metric_type
        self._description = description
        self._unit = unit
        self._default_labels = default_labels or {}

    def record(self, value: int | float, labels: dict[str, Any] | None = None) -> None:
        combined_labels = {**self._default_labels, **(labels or {})}
        logger.debug("metric recorded", metric_name=self.name, value=value, labels=combined_labels)
        self._record(value, combined_labels)

    @abstractmethod
    def _register(self, meter: metrics.Meter) -> None:
        pass

    @abstractmethod
    def _record(self, value: int | float, labels: dict[str, Any]) -> None:
        pass


class HistogramMetric(Metric):
    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "1",
        default_labels: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, metric_type, description, unit, default_labels)
        self._instance: metrics.Histogram | None = None

    @override
    def _register(self, meter: metrics.Meter) -> None:
        self._instance = meter.create_histogram(name=self.name, description=self._description, unit=self._unit)

    @override
    def _record(self, value: int | float, labels: dict[str, Any] | None = None) -> None:
        if self._instance:
            self._instance.record(value, attributes=labels)


class CounterMetric(Metric):
    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "1",
        default_labels: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, metric_type, description, unit, default_labels)
        self._instance: metrics.Counter | None = None

    @override
    def _register(self, meter: metrics.Meter) -> None:
        self._instance = meter.create_counter(name=self.name, description=self._description, unit=self._unit)

    @override
    def _record(self, value: int | float, labels: dict[str, Any] | None = None) -> None:
        if self._instance:
            self._instance.add(value, attributes=labels)


class TelemetryRegistry:
    METRIC_CONSTRUCTORS: dict[MetricType, Type[Metric]] = {
        MetricType.COUNTER: CounterMetric,
        MetricType.HISTOGRAM: HistogramMetric,
    }

    def __init__(self) -> None:
        self._default_labels: dict[str, Any] = {}
        self._metrics: dict[str, Metric] = {}
        self._meter: metrics.Meter | None = None
        self._tracer: trace.Tracer | None = None

    def initialize(
        self,
        meter_provider: MeterProvider | None = None,
        tracer_provider: TracerProvider | None = None,
        component_name: str = DEFAULT_NAME,
    ) -> None:
        if meter_provider:
            self._meter = metrics.get_meter(component_name, meter_provider=meter_provider)
            for metric in self._metrics.values():
                metric._register(self._meter)

        if tracer_provider:
            self._tracer = trace.get_tracer(component_name, tracer_provider=tracer_provider)

        logger.info(
            "initialized",
            default_labels=self._default_labels,
            number_of_metrics_registered=len(self._metrics),
        )

    def add_labels(self, labels: dict[str, Any]) -> None:
        if not labels:
            return
        self._default_labels.update(labels)
        logger.debug("default labels updated", default_labels=self._default_labels)

    def create_metric(self, metric_type: MetricType, name: str, description: str = "", unit: str = "1") -> None:
        if name in self._metrics:
            logger.warning("metric already exists", metric_name=name)
            return

        constructor = self.METRIC_CONSTRUCTORS.get(metric_type)
        if not constructor:
            raise KeyError(f"unsupported metric type: {metric_type}")

        metric = constructor(
            name=name, metric_type=metric_type, description=description, unit=unit, default_labels=self._default_labels
        )
        if self._meter:
            metric._register(self._meter)
        self._metrics[name] = metric

    def _get_tracer(self) -> trace.Tracer:
        if self._tracer:
            return self._tracer
        return NoOpTracer()

    def record_metric(self, name: str, value: int | float, labels: dict[str, Any] | None = None) -> None:
        if not self._meter:
            logger.debug("not yet initialized, cannot record metric", metric_name=name)
            return
        metric = self._metrics.get(name)
        if not metric:
            logger.warning("metric not found", metric_name=name)
            return
        metric.record(value, labels)

    def span(self, name: str, attributes: dict[str, Any] | None = None) -> AbstractContextManager[trace.Span]:
        tracer = self._get_tracer()
        merged_attributes = {**self._default_labels, **(attributes or {})}
        return tracer.start_as_current_span(name, attributes=merged_attributes)


telemetry = TelemetryRegistry()

__all__ = ["telemetry", "MetricType", "Metric", "HistogramMetric", "CounterMetric", "TelemetryRegistry"]
