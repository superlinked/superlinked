from superlinked import framework as sl


@sl.schema
class CarSchema:
    id: sl.IdField
    make: sl.String
    model: sl.String


car_schema = CarSchema()

car_make_text_space = sl.TextSimilaritySpace(text=car_schema.make, model="all-MiniLM-L6-v2")
car_model_text_space = sl.TextSimilaritySpace(text=car_schema.model, model="all-MiniLM-L6-v2")

index = sl.Index([car_make_text_space, car_model_text_space])

query = (
    sl.Query(index)
    .find(car_schema)
    .similar(car_make_text_space.text, sl.Param("make"))
    .similar(car_model_text_space.text, sl.Param("model"))
    .limit(sl.Param("limit"))
)

car_source: sl.RestSource = sl.RestSource(car_schema)

mongo_db_vector_database = sl.MongoDBVectorDatabase(
    "<USER>:<PASSWORD>@<HOST_URL>",
    "<DATABASE_NAME>",
    "<CLUSTER_NAME>",
    "<PROJECT_ID>",
    "<API_PUBLIC_KEY>",
    "<API_PRIVATE_KEY>",
)

executor = sl.RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[sl.RestQuery(sl.RestDescriptor("query"), query)],
    vector_database=mongo_db_vector_database,
)

sl.SuperlinkedRegistry.register(executor)
