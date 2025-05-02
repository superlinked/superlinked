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

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from superlinked.evaluation.storage_usage.data_stream_observer import DataStreamObserver
from superlinked.evaluation.storage_usage.exception import (
    UnsupportedIndexCountException,
    WorkflowException,
)
from superlinked.evaluation.storage_usage.storage_usage_report import (
    IndexedFieldInfo,
    PartialResultInfo,
    PartialResultSource,
    StorageUsageReport,
    StorageUsageReportDetail,
)
from superlinked.evaluation.storage_usage.vdb_watcher import VDBWatcher
from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.dsl.app.online.online_app import OnlineApp
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.online.source.online_source import OnlineSource


@dataclass
class TraceRoundInfo:
    title: str
    initial_vdb_memory_usage: int


class StorageUsageEvaluator:
    def __init__(self, app: OnlineApp[OnlineSource]) -> None:
        self.__app = app
        self.__index = self.__init_index(app)
        self.__data_stream_observer = DataStreamObserver()
        self.__vdb_watcher = VDBWatcher(self.__app.storage_manager._vdb_connector)
        self.__trace_round_info: TraceRoundInfo | None = None
        self.__report_details = list[StorageUsageReportDetail]()

    def __init_index(self, app: OnlineApp[OnlineSource]) -> Index:
        if (index_count := len(app._indices)) != 1:
            raise UnsupportedIndexCountException(f"Got {index_count}")
        return app._indices[0]

    def start_trace(self, title: str) -> None:
        self.__subscribe_to_data_streams()
        if self.__trace_round_info is not None:
            raise WorkflowException("Found ongoing tracing process, stop the previous one before starting a new one.")
        self.__trace_round_info = TraceRoundInfo(title, self.__vdb_watcher.get_memory_usage())

    def __subscribe_to_data_streams(self) -> None:
        for source in self.__app._sources:
            source.register_pre_transform(self.__data_stream_observer)

    def stop_trace(self) -> StorageUsageReportDetail:
        self.__unsubscribe_from_data_streams()
        if self.__trace_round_info is None:
            raise WorkflowException(
                "No ongoing tracing process was found. To start the evaluation, "
                + f"run {StorageUsageEvaluator.start_trace.__name__} first."
            )
        report_detail = self._detail_report(self.__data_stream_observer, self.__trace_round_info)
        self.__report_details.append(report_detail)
        self.__data_stream_observer.reset()
        self.__trace_round_info = None
        return report_detail

    def __unsubscribe_from_data_streams(self) -> None:
        for source in self.__app._sources:
            source.unregister_pre_transform(self.__data_stream_observer)

    def _detail_report(
        self, data_stream_observer: DataStreamObserver, trace_round_info: TraceRoundInfo
    ) -> StorageUsageReportDetail:
        memory_usage = self.__vdb_watcher.get_memory_usage() - trace_round_info.initial_vdb_memory_usage
        return StorageUsageReportDetail(
            title=trace_round_info.title,
            serialized_data_size=data_stream_observer.observed_size_bytes,
            immeasurable_messages_count=data_stream_observer.immeasurable_messages_count,
            indexed_field_types=self._get_indexed_field_types(self.__index),
            indexed_vector_size=self.__index._node.length,
            search_index_type=str(self.__app.storage_manager._vdb_connector.search_algorithm),
            partial_result_info=self._get_partial_result_info(self.__index._dag),
            memory_usage=memory_usage,
        )

    def _get_indexed_field_types(self, index: Index) -> list[IndexedFieldInfo]:
        return list(
            map(
                lambda item: IndexedFieldInfo(type_name=item[0], count=item[1]),
                Counter([type(field).__name__ for field in index._fields]).items(),
            )
        )

    def _get_partial_result_info(self, dag: Dag) -> list[PartialResultInfo]:
        return [
            PartialResultInfo(
                source=PartialResultSource.AN if isinstance(node, AggregationNode) else PartialResultSource.EAN,
                dimension=node.length,
            )
            for node in dag.nodes
            if isinstance(node, (AggregationNode, EventAggregationNode))
        ]

    def report(self) -> StorageUsageReport:
        return StorageUsageReport(report_details=self.__report_details)

    def report_to_csv(self, report_path: Path) -> None:
        self.report().to_csv(report_path)

    def clear_reports(self) -> None:
        self.__report_details.clear()
