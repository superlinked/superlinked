from superlinked.framework import (
    IdField,
    Index,
    MongoDBVectorDatabase,
    Param,
    Query,
    RestDescriptor,
    RestExecutor,
    RestQuery,
    RestSource,
    String,
    SuperlinkedRegistry,
    TextSimilaritySpace,
    schema,
)
@schema
class CarSchema:
    id: IdField
    make: String
    model: String


car_schema = CarSchema()

car_make_text_space = TextSimilaritySpace(text=car_schema.make, model="all-MiniLM-L6-v2")
car_model_text_space = TextSimilaritySpace(text=car_schema.model, model="all-MiniLM-L6-v2")

index = Index([car_make_text_space, car_model_text_space])

query = (
    Query(index)
    .find(car_schema)
    .similar(car_make_text_space.text, Param("make"))
    .similar(car_model_text_space.text, Param("model"))
    .limit(Param("limit"))
)

car_source: RestSource = RestSource(car_schema)

mongo_db_vector_database = MongoDBVectorDatabase(
    "<USER>:<PASSWORD>@<HOST_URL>",
    "<DATABASE_NAME>",
    "<CLUSTER_NAME>",
    "<PROJECT_ID>",
    "<API_PUBLIC_KEY>",
    "<API_PRIVATE_KEY>",
)

executor = RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=mongo_db_vector_database,
)

SuperlinkedRegistry.register(executor)
