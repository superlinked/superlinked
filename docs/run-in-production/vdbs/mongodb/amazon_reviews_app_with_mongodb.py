from superlinked import framework as sl

openai_config = sl.OpenAIClientConfig(api_key="YOUR_OPENAI_API_KEY", model="gpt-4o")


@sl.schema
class Review:
    id: sl.IdField
    review_text: sl.String
    rating: sl.Integer
    full_review_as_text: sl.String


review = Review()

review_text_space = sl.TextSimilaritySpace(text=review.review_text, model="all-MiniLM-L6-v2")
rating_maximizer_space = sl.NumberSpace(number=review.rating, min_value=1, max_value=5, mode=sl.Mode.MAXIMUM)
full_review_as_text_space = sl.TextSimilaritySpace(text=review.full_review_as_text, model="all-MiniLM-L6-v2")

naive_index = sl.Index([full_review_as_text_space])
advanced_index = sl.Index([review_text_space, rating_maximizer_space])

naive_query = (
    sl.Query(
        naive_index,
        weights={full_review_as_text_space: sl.Param("full_review_as_text_weight")},
    )
    .find(review)
    .similar(full_review_as_text_space.text, sl.Param("query_text"))
    .limit(sl.Param("limit"))
    .with_natural_query(sl.Param("natural_query"), openai_config)
)
superlinked_query = (
    sl.Query(
        advanced_index,
        weights={
            review_text_space: sl.Param("review_text_weight"),
            rating_maximizer_space: sl.Param("rating_maximizer_weight"),
        },
    )
    .find(review)
    .similar(review_text_space.text, sl.Param("query_text"))
    .limit(sl.Param("limit"))
    .with_natural_query(sl.Param("natural_query"), openai_config)
)


review_source: sl.RestSource = sl.RestSource(review)
review_data_loader = sl.DataLoaderConfig(
    "https://storage.googleapis.com/superlinked-sample-datasets/amazon_dataset_ext_1000.jsonl",
    sl.DataFormat.JSON,
    pandas_read_kwargs={"lines": True, "chunksize": 100},
)
review_loader_source: sl.DataLoaderSource = sl.DataLoaderSource(review, review_data_loader)
mongo_db_vector_database = sl.MongoDBVectorDatabase(
    "<USER>:<PASSWORD>@<HOST_URL>",
    "<DATABASE_NAME>",
    "<CLUSTER_NAME>",
    "<PROJECT_ID>",
    "<API_PUBLIC_KEY>",
    "<API_PRIVATE_KEY>",
)
executor = sl.RestExecutor(
    sources=[review_source, review_loader_source],
    indices=[naive_index, advanced_index],
    queries=[
        sl.RestQuery(sl.RestDescriptor("naive_query"), naive_query),
        sl.RestQuery(sl.RestDescriptor("superlinked_query"), superlinked_query),
    ],
    vector_database=mongo_db_vector_database,
)

sl.SuperlinkedRegistry.register(executor)
