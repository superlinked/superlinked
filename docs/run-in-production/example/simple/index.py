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
