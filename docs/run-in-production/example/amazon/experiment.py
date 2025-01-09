from datetime import datetime, timezone

from superlinked import framework as sl

from .index import index, review
from .query import query

START_OF_2024_TS = int(datetime(2024, 1, 2, tzinfo=timezone.utc).timestamp())
EXECUTOR_DATA = {sl.CONTEXT_COMMON: {sl.CONTEXT_COMMON_NOW: START_OF_2024_TS}}

source: sl.InMemorySource = sl.InMemorySource(review)

executor = sl.InMemoryExecutor(
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
