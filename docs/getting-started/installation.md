---
# description: >-
icon: display
---

# Installation

### In a notebook
Install the superlinked library:

```python
%pip install superlinked
```


### As a script
Ensure your python version is at least `3.10.x` but not newer than `3.12.x`.

```bash
$> python -V
Python 3.10.9
```

If your python version is not `>=3.10` and `<=3.12` you might use [pyenv](https://github.com/pyenv/pyenv) to install it.

Upgrade pip and install the superlinked library.

```bash
$> python -m pip install --upgrade pip
$> python -m pip install superlinked
```

### Run the example

{% hint style="info" %}
First run will take slightly longer as it has to download the embedding model.
{% endhint %}


```python   
import json

from superlinked.framework.common.embedding.number_embedding import Mode
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.parser.dataframe_parser import DataFrameParser
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import Integer, String
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.dsl.space.number_space import NumberSpace
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryExecutor,
)


@schema
class Review:
    id: IdField
    review_text: String
    rating: Integer


review = Review()

review_text_space = TextSimilaritySpace(
    text=review.review_text, model="Alibaba-NLP/gte-large-en-v1.5"
)
rating_maximizer_space = NumberSpace(
    number=review.rating, min_value=1, max_value=5, mode=Mode.MAXIMUM
)
index = Index([review_text_space, rating_maximizer_space], fields=[review.rating])

# fill this with your API key - this will drive param extraction
openai_config = OpenAIClientConfig(api_key="YOUR_OPENAI_API_KEY", model="gpt-4o")

# it is possible now to add descriptions to a `Param` to aid the parsing of information from natural language queries.
text_similar_param = Param(
    "query_text",
    description="The text in the user's query that is used to search in the reviews' body. Extract info that does apply to other spaces or params.",
)

# Define your query using dynamic parameters for query text and weights.
# we will have our LLM fill them based on our natural language query
query = (
    Query(
        index,
        weights={
            review_text_space: Param("review_text_weight"),
            rating_maximizer_space: Param("rating_maximizer_weight"),
        },
    )
    .find(review)
    .similar(
        review_text_space.text,
        text_similar_param,
    )
    .limit(Param("limit"))
    .with_natural_query(Param("natural_query"), openai_config)
)

# Run the app.
source: InMemorySource = InMemorySource(review)
executor = InMemoryExecutor(sources=[source], indices=[index])
app = executor.run()

# Download dataset.
data = [
    {"id": 1, "review_text": "Useless product", "rating": 1},
    {"id": 2, "review_text": "Great product I am so happy!", "rating": 5},
    {"id": 3, "review_text": "Mediocre stuff fits the purpose", "rating": 3},
]

# Ingest data to the framework.
source.put(data)

result = app.query(query, natural_query="Show me the best product", limit=1)

# examine the extracted parameters from your query
print(json.dumps(result.knn_params, indent=2))
# the result is the 5 star rated product
result.to_pandas()
```