# Superlinked 

<div align="center">

![PyPI](https://img.shields.io/pypi/v/superlinked)
![Last commit](https://img.shields.io/github/last-commit/superlinked/superlinked)
![License](https://img.shields.io/github/license/superlinked/superlinked) 
![](https://img.shields.io/github/stars/superlinked/superlinked)

</div>

<div align="center">

[Experiment in a notebook](#try-in-a-notebook)  | [Run in production](#run-in-production) | [Use-cases](#use-cases) | [Supported VDBs](#supported-vdbs) | [Resources](#resources)

</div>

Superlinked is a compute framework for your information retrieval and feature engineering systems, focused on turning complex (structured+unstructured) data into ultra-modal vector embeddings within your RAG, Search, Recommendations and Analytics stack. Integrate Superlinked into your machine learning stack for custom model performance with pre-trained model convenience. 

If you like what we do, give us a star! ⭐

![](https://storage.googleapis.com/superlinked-public-assets/readme.png)

Visit [Superlinked](https://superlinked.com/) for more information about the company behind this product and our other initiatives.

## Features

- Embed structured and unstructured data ([Text](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/text_embedding.ipynb) | [Number](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/number_embedding_minmax.ipynb) | [Category](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/categorical_embedding.ipynb) | [Time](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/recency_embedding.ipynb) | [Event](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/event_effects.ipynb))
- Create your custom encoder ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/custom_space.ipynb))
- Combine your encoders ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/combine_multiple_embeddings.ipynb))
- Use query-time weights ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/query_time_weights.ipynb))
- Filter your results ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/hard_filtering.ipynb))
- Use dynamic parameters ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/dynamic_parameters.ipynb))
- Sample your vectors ([notebook](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/vector_sampler.ipynb))

You can check a full list of our [features](https://github.com/superlinked/superlinked/tree/main/notebook/feature) or head to our [reference](#reference) section for more information.

## Use-cases

Dive deeper with our notebooks into how each use-case benefits from the Superlinked framework.

- **RAG**: [HR Knowledgebase](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/rag_hr_knowledgebase.ipynb)
- **Semantic Search**: [Movies](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/semantic_search_netflix_titles.ipynb), [Business News](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/semantic_search_news.ipynb)
- **Recommendation Systems**: [E-commerce](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/recommendations_e_commerce.ipynb)
- **Analytics**: [User Acquisition](https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/analytics_user_acquisition.ipynb), [Keyword expansion](https://github.com/superlinked/superlinked/blob/main/notebook/analytics_keyword_expansion_ads.ipynb)

You can check a full list of examples [here](https://colab.research.google.com/github/superlinked/superlinked/tree/main/notebook).

## Experiment in a notebook

Example on combining Text with Numerical encoders to get correct results with LLMs.

#### Install the superlinked library
```
%pip install superlinked
```

#### Run the example:

>First run will take slightly longer as it has to download the embedding model.  

```python
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import InMemoryExecutor


@schema # Describe your schemas.
class Document:
    id: IdField  # Each schema should have exactly one `IdField`.
    body: String # Use `String` for text fields.

document = Document()

relevance_space = TextSimilaritySpace(text=document.body, model="sentence-transformers/all-mpnet-base-v2") # Select your semantic embedding model.
document_index = Index([relevance_space]) # Combine your spaces to a queryable index.

query = Query(document_index).find(document).similar(relevance_space.text, Param("query_text")) # Define your query with dynamic parameters.

source: InMemorySource = InMemorySource(document) # Connect a data source to your schema.

executor = InMemoryExecutor(sources=[source], indices=[document_index]) # Tie it all together to run your configuration.
app = executor.run()

source.put([{"id": "happy_dog", "body": "That is a happy dog"}])
source.put([{"id": "happy_person", "body": "That is a very happy person"}])
source.put([{"id": "sunny_day", "body": "Today is a sunny day"}])

print(app.query(query, query_text="Who is a positive friend?")) # Run your query.
```

## Run in production

[Superlinked Server](https://github.com/superlinked/superlinked/tree/main/server) allows you to leverage the power of Superlinked in deployable projects. With a single script, you can deploy a Superlinked-powered app instance that creates REST endpoints and connects to external Vector Databases. This makes it an ideal solution for those seeking an easy-to-deploy environment for their Superlinked projects.

If your are interested in learning more about running at scale, [Book a demo](https://superlinked.typeform.com/to/LXMRzHWk) for an early access to our managed cloud.

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

You can check the full list [here](https://github.com/superlinked/superlinked/tree/main/framework/reference).

## Resources

- [Vector DB Comparison](https://superlinked.com/vector-db-comparison/): Open-source collaborative comparison of vector databases by Superlinked.
- [Vector Hub](https://superlinked.com/vectorhub/): VectorHub is a free and open-sourced learning hub for people interested in adding vector retrieval to their ML stack

## Support

If you encounter any challenges during your experiments, feel free to create an [issue](https://github.com/superlinked/superlinked/issues/new?assignees=kembala&labels=bug&projects=&template=bug_report.md&title=), request a [feature](https://github.com/superlinked/superlinked/issues/new?assignees=kembala&labels=enhancement&projects=&template=feature_request.md&title=) or to [start a discussion](https://github.com/superlinked/superlinked/discussions/new/choose).
Make sure to group your feedback in separate issues and discussions by topic. Thank you for your feedback!