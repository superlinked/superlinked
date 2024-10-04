from datetime import timedelta

from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import Integer, String, StringList, Timestamp
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.number_space import Mode, NumberSpace
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace


@schema
class Review:
    rating: Integer
    timestamp: Timestamp
    verified_purchase: StringList
    review_text: String
    id: IdField


review = Review()


rating_space = NumberSpace(review.rating, min_value=1, max_value=5, mode=Mode.MAXIMUM)
recency_space = RecencySpace(review.timestamp, period_time_list=PeriodTime(timedelta(days=3650)))
verified_category_space = CategoricalSimilaritySpace(
    review.verified_purchase,
    categories=["True", "False"],
    uncategorized_as_category=False,
    negative_filter=-5,
)
relevance_space = TextSimilaritySpace(review.review_text, model="sentence-transformers/all-mpnet-base-v2")

index = Index([relevance_space, recency_space, rating_space, verified_category_space])
