from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace


@schema
class YourSchema:
    id: IdField
    attribute: String


your_schema = YourSchema()

model_name = "<your model name goes here>"  # Ensure that you replace this with a valid model name!
text_space = TextSimilaritySpace(text=your_schema.attribute, model=model_name)

index = Index(text_space)
