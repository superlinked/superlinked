from datetime import datetime, timezone

from superlinked.framework.common.dag.context import CONTEXT_COMMON, CONTEXT_COMMON_NOW
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.data_loader_source import DataFormat, DataLoaderConfig, DataLoaderSource
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase

from .index import index, review
from .query import query

START_OF_2024_TS = int(datetime(2024, 1, 2, tzinfo=timezone.utc).timestamp())
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: START_OF_2024_TS}}

source: RestSource = RestSource(review)

config = DataLoaderConfig(
    "https://storage.googleapis.com/superlinked-preview-test-data/amazon_dataset_1000.jsonl",
    DataFormat.JSON,
    pandas_read_kwargs={"lines": True},
)
loader_source: DataLoaderSource = DataLoaderSource(review, config)

executor = RestExecutor(
    sources=[source, loader_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
    context_data=EXECUTOR_DATA,
)

SuperlinkedRegistry.register(executor)
