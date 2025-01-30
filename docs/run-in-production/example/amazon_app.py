from datetime import datetime, timedelta, timezone

from superlinked import framework as sl

START_OF_2024_TS = int(datetime(2024, 1, 2, tzinfo=timezone.utc).timestamp())
EXECUTOR_DATA = {sl.CONTEXT_COMMON: {sl.CONTEXT_COMMON_NOW: START_OF_2024_TS}}


@sl.schema
class Review:
    rating: sl.Integer
    timestamp: sl.Timestamp
    verified_purchase: sl.StringList
    review_text: sl.String
    id: sl.IdField


review = Review()


rating_space = sl.NumberSpace(review.rating, min_value=1, max_value=5, mode=sl.Mode.MAXIMUM)
recency_space = sl.RecencySpace(review.timestamp, period_time_list=sl.PeriodTime(timedelta(days=3650)))
verified_category_space = sl.CategoricalSimilaritySpace(
    review.verified_purchase,
    categories=["True", "False"],
    uncategorized_as_category=False,
    negative_filter=-5,
)
relevance_space = sl.TextSimilaritySpace(review.review_text, model="sentence-transformers/all-mpnet-base-v2")

index = sl.Index([relevance_space, recency_space, rating_space, verified_category_space])

source: sl.RestSource = sl.RestSource(review)


query = (
    sl.Query(
        index,
        weights={
            rating_space: sl.Param("rating_weight"),
            recency_space: sl.Param("recency_weight"),
            verified_category_space: sl.Param("verified_category_weight"),
            relevance_space: sl.Param("relevance_weight"),
        },
    )
    .find(review)
    .similar(relevance_space.text, sl.Param("query_text"))
    .similar(verified_category_space.category, sl.Param("query_verified"))
    .select_all()
)

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
