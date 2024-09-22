<div align="center">
<picture>
  <source
    srcset="https://cdn.prod.website-files.com/65dce6831bf9f730421e2915/66ef0317ed8616151ee1d451_superlinked_logo_white.png"
    media="(prefers-color-scheme: dark)"
  />
  <source
    srcset="https://cdn.prod.website-files.com/65dce6831bf9f730421e2915/65dce6831bf9f730421e2929_superlinked_logo.svg"
    media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)"
  />
  <img width=400 src="https://cdn.prod.website-files.com/65dce6831bf9f730421e2915/66ef0317ed8616151ee1d451_superlinked_logo_white.png" />
</picture>

</div>  &nbsp;

<div align="center">

![PyPI](https://img.shields.io/pypi/v/superlinked)
![Last commit](https://img.shields.io/github/last-commit/superlinked/superlinked)
![License](https://img.shields.io/github/license/superlinked/superlinked) 
![](https://img.shields.io/github/stars/superlinked/superlinked)

</div>

<div align="center">

[Experiment in a notebook](#experiment-in-a-notebook)  | [Run in production](#run-in-production) | [Use-cases](#use-cases) | [Supported VDBs](#supported-vdbs) | [Resources](#resources)

</div>

#### Why use Superlinked
Improve your vector search relevance by encoding your metadata together with your data into your vector embeddings.

#### What is Superlinked
Superlinked is a framework AND a self-hostable REST API server that helps you make better vectors, that sits between your data, vector database and backend services.

#### How does it work
Superlinked makes it easy to construct custom data & query embedding models from pre-trained encoders, see the <b>feature</b> and <b>use-case</b> notebooks below for examples.

If you like what we do, give us a star! ⭐

![](https://cdn.prod.website-files.com/65dce6831bf9f730421e2915/66f05365ad05806eb16c9cb8_superlinked_system_diagram3.png)

Visit [Superlinked](https://superlinked.com/) for more information about the company behind this product and our other initiatives.

## Features

- Embed structured and unstructured data ([Text](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/text_embedding.ipynb) | [Number](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/number_embedding_minmax.ipynb) | [Category](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/categorical_embedding.ipynb) | [Time](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/recency_embedding.ipynb) | [Event](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/event_effects.ipynb))
- Combine encoders to build a custom model ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/combine_multiple_embeddings.ipynb))
- Add a custom encoder ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/custom_space.ipynb))
- Update your vectors with behavioral events & relationships ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/event_effects.ipynb))
- Use query-time weights ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/query_time_weights.ipynb))
- Query with natural language ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/natural_language_querying.ipynb))
- Filter your results ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/hard_filtering.ipynb))
- Export vectors for analysis ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/vector_sampler.ipynb))

You can check a full list of our [features](https://github.com/superlinked/superlinked/tree/main/notebook/feature) or head to our [reference](#reference) section for more information.

## Use-cases

Dive deeper with our notebooks into how each use-case benefits from the Superlinked framework.

- **RAG**: [HR Knowledgebase](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/rag_hr_knowledgebase.ipynb)
- **Semantic Search**: [Movies](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/semantic_search_netflix_titles.ipynb), [Business News](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/semantic_search_news.ipynb), [Product Images & Descriptions](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/image_search_e_commerce.ipynb)
- **Recommendation Systems**: [E-commerce](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/recommendations_e_commerce.ipynb)
- **Analytics**: [User Acquisition](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/analytics_user_acquisition.ipynb), [Keyword expansion](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/analytics_keyword_expansion_ads.ipynb)

You can check a full list of examples [here](https://github.com/superlinked/superlinked/tree/main/notebook).

## Experiment in a notebook

Example on combining Text with Numerical encoders to get correct results with LLMs.

#### Install the superlinked library
```
%pip install superlinked
```

#### Run the example:

>First run will take slightly longer as it has to download the embedding model.  

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
openai_config = OpenAIClientConfig(
    api_key="YOUR_OPENAI_API_KEY", model="gpt-4o"
)

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

## Run in production

[Superlinked Server](https://github.com/superlinked/superlinked/tree/main/server) allows you to leverage the power of Superlinked in deployable projects. With a single script, you can deploy a Superlinked-powered app instance that creates REST endpoints and connects to external Vector Databases. This makes it an ideal solution for those seeking an easy-to-deploy environment for their Superlinked projects.

If your are interested in learning more about running at scale, [Book a demo](https://links.superlinked.com/sl-repo-readme-form) for an early access to our managed cloud.

### Supported VDBs

We have started partnering with vector database providers to allow you to use Superlinked with your VDB of choice. If you are unsure, which VDB to chose, check-out our [Vector DB Comparison](https://superlinked.com/vector-db-comparison/).

- [Redis](https://github.com/superlinked/superlinked/tree/main/server/docs/redis/redis.md)
- [MongoDB](https://github.com/superlinked/superlinked/tree/main/server/docs/mongodb/mongodb.md)

Missing your favorite VDB? [Tell us which vector database we should support next!](https://github.com/superlinked/superlinked/discussions/41)

## Reference

1. Describe your data using Python classes with the [@schema](https://github.com/superlinked/superlinked/blob/main/framework/reference/common/schema/schema.md) decorator.
2. Describe your vector embeddings from building blocks with [Spaces](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/space/index.md).
3. Combine your embeddings into a queryable [Index](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/index/index.m.md).
4. Define your search with dynamic parameters and weights as a [Query](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/query/query.md).
5. Load your data using a [Source](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/source/index.md).
6.  Define your transformations with a [Parser](https://github.com/superlinked/superlinked/blob/main/framework/reference/common/parser) (e.g.: from [`pd.DataFrame`](https://github.com/superlinked/superlinked/blob/main/framework/reference/common/parser/dataframe_parser.md)). 
7. Run your configuration with an [Executor](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/executor/in_memory/in_memory_executor.md).

You can check all references [here](https://github.com/superlinked/superlinked/tree/main/framework/reference).

## Logging

Contextual information is automatically included in log messages, such as the process ID and package scope. Personally Identifiable Information (PII) is filtered out by default but can be exposed with the `SUPERLINKED_EXPOSE_PII` environment variable to `true`.

## Resources

- [Vector DB Comparison](https://superlinked.com/vector-db-comparison/): Open-source collaborative comparison of vector databases by Superlinked.
- [Vector Hub](https://superlinked.com/vectorhub/): VectorHub is a free and open-sourced learning hub for people interested in adding vector retrieval to their ML stack

## Support

If you encounter any challenges during your experiments, feel free to create an [issue](https://github.com/superlinked/superlinked/issues/new?assignees=kembala&labels=bug&projects=&template=bug_report.md&title=), request a [feature](https://github.com/superlinked/superlinked/issues/new?assignees=kembala&labels=enhancement&projects=&template=feature_request.md&title=) or to [start a discussion](https://github.com/superlinked/superlinked/discussions/new/choose).
Make sure to group your feedback in separate issues and discussions by topic. Thank you for your feedback!
