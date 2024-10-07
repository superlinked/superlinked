from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace


@schema
class CarSchema:
    id: IdField
    make: String
    model: String


car_schema = CarSchema()

car_make_text_space = TextSimilaritySpace(text=car_schema.make, model="all-MiniLM-L6-v2")
car_model_text_space = TextSimilaritySpace(text=car_schema.model, model="all-MiniLM-L6-v2")

index = Index([car_make_text_space, car_model_text_space])
