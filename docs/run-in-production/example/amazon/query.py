from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query

from .index import index, rating_space, recency_space, relevance_space, review, verified_category_space

query = (
    Query(
        index,
        weights={
            rating_space: Param("rating_weight"),
            recency_space: Param("recency_weight"),
            verified_category_space: Param("verified_category_weight"),
            relevance_space: Param("relevance_weight"),
        },
    )
    .find(review)
    .similar(relevance_space.text, Param("query_text"))
    .similar(verified_category_space.category, Param("query_verified"))
)
