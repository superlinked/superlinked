# Superlinked 

Superlinked is a declarative Python SDK that enables you to turn complex data into vectors, in a way that fits the modern data stack and works with your favorite Vector Databases.

3 key areas of focus:

1. Custom embedding model creation that fits your complex data entities.
1. ETL for your vector index for both streaming and batch use-cases.
1. Vector-native query language that helps you convert hybrid search queries to pure vector queries.

Visit [Superlinked](https://superlinked.com/) for more information about the company behind this product and our other initiatives.

## Use-cases

- [E-commerce Recommendation System](https://github.com/superlinked/superlinked-alpha/blob/main/notebook/recommendations_e_commerce.ipynb)
- [Movie Recommendations](https://github.com/superlinked/superlinked-alpha/blob/main/notebook/semantic_search_netflix_titles.ipynb)
- [Semantic Search](https://github.com/superlinked/superlinked-alpha/blob/main/notebook/semantic_search_news.ipynb)

## Reference

1. Describe your data using Python classes with the [@schema](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/common/schema/schema.md) decorator.
2. Describe your vector embeddings from building blocks with [Spaces](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/dsl/space/index.md).
3. Combine your embeddings into a queryable [Index](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/dsl/index/index.m.md).
4. Define your search with dynamic parameters and weights as a [Query](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/dsl/query/query.md).
5. Load your data using a [Source](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/dsl/source/index.md).
6. Define your transformations with a [Parser](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/common/parser) (e.g.: from [`pd.DataFrame`](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/common/parser/dataframe_parser.md)). 
7. Run your configuration with an [Executor](https://github.com/superlinked/superlinked-alpha/blob/main/docs/superlinked/framework/dsl/executor/in_memory/in_memory_executor.md).
  
## Example code

Example on how to use Superlinked in a notebook to experiment with the semantic search use-case.

```python
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String, Timestamp
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import InMemoryExecutor


@schema # Desribe your schemas.
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

Ready to go to production? We are launching our first Vector DB connectors soon! [Tell us which Vector DB we should support!](https://github.com/superlinked/superlinked-alpha/discussions/41)

## Articles

- [Vector DB Comparison](https://superlinked.com/vector-db-comparison/): Open-source collaboritve comparison of vector databases by Superlinked.
- [Vector Hub](https://superlinked.com/vectorhub/): VectorHub is a free and open-sourced learning hub for people interested in adding vector retrieval to their ML stack

## Support

If you encounter any challanges during your experiments, feel free to create an [issue](https://github.com/superlinked/superlinked-alpha/issues/new?assignees=ClaireSuperlinked&labels=bug&projects=&template=bug_report.md&title=), request a [feature](https://github.com/superlinked/superlinked-alpha/issues/new?assignees=ClaireSuperlinked&labels=enhancement&projects=&template=feature_request.md&title=) or to [start a discussion](https://github.com/superlinked/superlinked-alpha/discussions/new/choose).
Make sure to group your feedback in separate issues and discussions by topic. Thank you for your feedback!
