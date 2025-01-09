from datetime import timedelta

from superlinked import framework as sl


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
