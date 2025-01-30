from superlinked import framework as sl

from .index import index, rating_space, recency_space, relevance_space, review, verified_category_space

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
