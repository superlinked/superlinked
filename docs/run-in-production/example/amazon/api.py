from datetime import datetime, timezone

from superlinked import framework as sl

from .index import index, review
from .query import query

START_OF_2024_TS = int(datetime(2024, 1, 2, tzinfo=timezone.utc).timestamp())
EXECUTOR_DATA = {sl.CONTEXT_COMMON: {sl.CONTEXT_COMMON_NOW: START_OF_2024_TS}}

source: sl.RestSource = sl.RestSource(review)

config = sl.DataLoaderConfig(
    "https://storage.googleapis.com/superlinked-preview-test-data/amazon_dataset_1000.jsonl",
    sl.DataFormat.JSON,
    pandas_read_kwargs={"lines": True},
)
loader_source: sl.DataLoaderSource = sl.DataLoaderSource(review, config)

executor = sl.RestExecutor(
    sources=[source, loader_source],
    indices=[index],
    queries=[sl.RestQuery(sl.RestDescriptor("query"), query)],
    vector_database=sl.InMemoryVectorDatabase(),
    context_data=EXECUTOR_DATA,
)

sl.SuperlinkedRegistry.register(executor)
