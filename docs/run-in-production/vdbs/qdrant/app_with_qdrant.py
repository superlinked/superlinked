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
    .select_all()
    .limit(sl.Param("limit"))
)

car_source: sl.RestSource = sl.RestSource(car_schema)

qdrant_vector_database = sl.QdrantVectorDatabase("<HOST_URL>", "API_KEY")

executor = sl.RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[sl.RestQuery(sl.RestDescriptor("query"), query)],
    vector_database=qdrant_vector_database,
)

sl.SuperlinkedRegistry.register(executor)
