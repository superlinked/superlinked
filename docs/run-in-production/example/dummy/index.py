from superlinked import framework as sl


@sl.schema
class YourSchema:
    id: sl.IdField
    attribute: sl.String


your_schema = YourSchema()

MODEL_NAME = "<your model name goes here>"  # Ensure that you replace this with a valid model name!
text_space = sl.TextSimilaritySpace(text=your_schema.attribute, model=MODEL_NAME)

index = sl.Index(text_space)
