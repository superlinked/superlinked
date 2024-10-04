from datetime import datetime, timezone

from superlinked.framework.common.dag.context import CONTEXT_COMMON, CONTEXT_COMMON_NOW
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import InMemoryExecutor
from superlinked.framework.dsl.source.in_memory_source import InMemorySource

from .index import index, review
from .query import query

START_OF_2024_TS = int(datetime(2024, 1, 2, tzinfo=timezone.utc).timestamp())
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: START_OF_2024_TS}}

source: InMemorySource = InMemorySource(review)

executor = InMemoryExecutor(
    sources=[source],
    indices=[index],
    context_data=EXECUTOR_DATA,
)

app = executor.run()

source.put(
    [
        {
            "id": "test_id",
            "rating": 7,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "verified_purchase": "True",
            "review_text": "This is a review",
        }
    ]
)

result = app.query(query)

print(result)
