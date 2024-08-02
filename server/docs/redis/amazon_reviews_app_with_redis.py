from superlinked.framework.common.embedding.number_embedding import Mode
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import Integer, String
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.data_loader_source import DataFormat, DataLoaderConfig, DataLoaderSource
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.space.number_space import NumberSpace
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.storage.redis_vector_database import RedisVectorDatabase

openai_config = OpenAIClientConfig(api_key="YOUR_OPENAI_API_KEY", model="gpt-4o")


@schema
class Review:
    id: IdField
    review_text: String
    rating: Integer
    full_review_as_text: String


review = Review()

review_text_space = TextSimilaritySpace(text=review.review_text, model="all-MiniLM-L6-v2")
rating_maximizer_space = NumberSpace(number=review.rating, min_value=1, max_value=5, mode=Mode.MAXIMUM)
full_review_as_text_space = TextSimilaritySpace(text=review.full_review_as_text, model="all-MiniLM-L6-v2")

naive_index = Index([full_review_as_text_space])
advanced_index = Index([review_text_space, rating_maximizer_space])

naive_query = (
    Query(
        naive_index,
        weights={full_review_as_text_space: Param("full_review_as_text_weight")},
    )
    .find(review)
    .similar(full_review_as_text_space.text, Param("query_text"))
    .limit(Param("limit"))
    .with_natural_query(Param("natural_query"), openai_config)
)
superlinked_query = (
    Query(
        advanced_index,
        weights={
            review_text_space: Param("review_text_weight"),
            rating_maximizer_space: Param("rating_maximizer_weight"),
        },
    )
    .find(review)
    .similar(review_text_space.text, Param("query_text"))
    .limit(Param("limit"))
    .with_natural_query(Param("natural_query"), openai_config)
)


review_source: RestSource = RestSource(review)
review_data_loader = DataLoaderConfig(
    "https://storage.googleapis.com/superlinked-sample-datasets/amazon_dataset_ext_1000.jsonl",
    DataFormat.JSON,
    pandas_read_kwargs={"lines": True, "chunksize": 100},
)
review_loader_source: DataLoaderSource = DataLoaderSource(review, review_data_loader)
redis_vector_database = RedisVectorDatabase("<HOST_URL>", 12345, username="default", password="<password>")
executor = RestExecutor(
    sources=[review_source, review_loader_source],
    indices=[naive_index, advanced_index],
    queries=[
        RestQuery(RestDescriptor("naive_query"), naive_query),
        RestQuery(RestDescriptor("superlinked_query"), superlinked_query),
    ],
    vector_database=redis_vector_database,
)

SuperlinkedRegistry.register(executor)
