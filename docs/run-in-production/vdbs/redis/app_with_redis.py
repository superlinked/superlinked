from superlinked.framework import (
    IdField,
    Index,
    Param,
    RedisVectorDatabase,
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

redis_vector_database = RedisVectorDatabase("<HOST_URL>", 12345, username="default", password="<password>")

executor = RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=redis_vector_database,
)

SuperlinkedRegistry.register(executor)
