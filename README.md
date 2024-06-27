# Superlinked 

<div align="center">

![GitHub](https://img.shields.io/github/license/superlinked/superlinked) ![GitHub last commit](https://img.shields.io/github/last-commit/superlinked/superlinked)

</div>


Superlinked is a compute framework for your information retrieval and feature engineering systems, focused on turning complex data into vector embeddings within your RAG, Search, RecSys and Analytics stack. Integrate Superlinked into your machine learning stack for custom model performance with pre-trained model convenience. 

If you like what we do, give us a star! ⭐

The screenshot below shows how to build multimodal vectors from your data & define weights at query time to avoid postprocessing & rerank requirements.

![If the image does not render, you can check the notebook here: https://github.com/superlinked/superlinked/blob/main/notebook/recommendations_e_commerce.ipynb](https://storage.googleapis.com/superlinked-public-assets/notebook.png)

Our current release allows you to explore our computational model in simple scripts and python notebooks, our next major release will focus on helping you run Superlinked in production, with built-in data infra and vector database integrations.

Visit [Superlinked](https://superlinked.com/) for more information about the company behind this product and our other initiatives.

## Try it out

Example on how to use Superlinked to experiment with the semantic search use-case. 

### Pre-requisites

#### In a notebook

Install the superlinked library: 
```
%pip install superlinked
```

#### As a script 
Ensure your python version is at least 3.10.x but not newer than 3.12.

```commandline
$> python -V
Python 3.10.9
```

If your python version is not `3.10.x` you might use [pyenv](https://github.com/pyenv/pyenv) to install it. 

Upgrade pip and install the superlinked library.

```commandline
$> python -m pip install --upgrade pip
$> python -m pip install superlinked
```

### Run the example

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

Ready to go to production? We are launching our first Vector DB connectors soon! [Tell us which Vector DB we should support!](https://github.com/superlinked/superlinked/discussions/41)

## Use-cases

- **RAG**: [HR Knowledgebase](https://github.com/superlinked/superlinked/blob/main/notebook/rag_hr_knowledgebase.ipynb)
- **Semantic Search**: [Movies](https://github.com/superlinked/superlinked/blob/main/notebook/semantic_search_netflix_titles.ipynb), [Business News](https://github.com/superlinked/superlinked/blob/main/notebook/semantic_search_news.ipynb)
- **Recommendation Systems**: [E-commerce](https://github.com/superlinked/superlinked/blob/main/notebook/recommendations_e_commerce.ipynb)
- **Analytics**: [User Acquisition](https://github.com/superlinked/superlinked/blob/main/notebook/analytics_user_acquisition.ipynb)

You can check a full list of examples [here](https://github.com/superlinked/superlinked/tree/main/notebook).

## Reference

1. Describe your data using Python classes with the [@schema](https://github.com/superlinked/superlinked/blob/main/framework/reference/common/schema/schema.md) decorator.
2. Describe your vector embeddings from building blocks with [Spaces](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/space/index.md).
3. Combine your embeddings into a queryable [Index](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/index/index.m.md).
4. Define your search with dynamic parameters and weights as a [Query](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/query/query.md).
5. Load your data using a [Source](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/source/index.md).
6. Define your transformations with a [Parser](https://github.com/superlinked/superlinked/blob/main/framework/reference/common/parser) (e.g.: from [`pd.DataFrame`](https://github.com/superlinked/superlinked/blob/main/framework/reference/common/parser/dataframe_parser.md)). 
7. Run your configuration with an [Executor](https://github.com/superlinked/superlinked/blob/main/framework/reference/dsl/executor/in_memory/in_memory_executor.md).

You can check a list of our [features](https://github.com/superlinked/superlinked/tree/main/notebook/feature) or head to our [documentation](https://github.com/superlinked/superlinked/tree/main/docs).
  
## Articles

- [Vector DB Comparison](https://superlinked.com/vector-db-comparison/): Open-source collaborative comparison of vector databases by Superlinked.
- [Vector Hub](https://superlinked.com/vectorhub/): VectorHub is a free and open-sourced learning hub for people interested in adding vector retrieval to their ML stack

## Support

If you encounter any challenges during your experiments, feel free to create an [issue](https://github.com/superlinked/superlinked/issues/new?assignees=ClaireSuperlinked&labels=bug&projects=&template=bug_report.md&title=), request a [feature](https://github.com/superlinked/superlinked/issues/new?assignees=ClaireSuperlinked&labels=enhancement&projects=&template=feature_request.md&title=) or to [start a discussion](https://github.com/superlinked/superlinked/discussions/new/choose).
Make sure to group your feedback in separate issues and discussions by topic. Thank you for your feedback!


