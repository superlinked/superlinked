---
description: How you can use Superlinked to achieve quality retrieval, by implementing query time weights - at both query definition and query execution.
icon: dumbbell
---

# Query time weights & why you should care

Getting quality results from vector database queries isn’t easy. Our experience in machine learning deployment for production use cases has revealed two basic things about representing data:
1. the richer your source dataset, the better your chances of getting good results, provided your embeddings sufficiently represent your dataset
2. different use cases make different parts of your overall dataset more important
Any system that achieves efficient, high quality retrieval has to capture the richness of your source dataset, and prioritize the parts of your data that fit your use case.

At Superlinked, we use our Spaces class (discussed in detail [here](multiple-embeddings.md)) to create embeddings for different data attributes rather than using a text embedding model to ingest all of the data we have on an entity indiscriminately as single piece of text. By concatenating these attribute-specific vectors into a rich multimodal vector, we can achieve better results on the first search, obviating the need for time-consuming reranking and complex custom layers later on.

But the other crucial retrieval-improving element in the Superlinked approach is query time weighting. We empower you to prioritize those parts of your data that are most important for your use case/s by keeping all weights on the query side vector - you can experiment and fine-tune your retrieval without having to re-embed and re-index your dataset.

Let’s walk through how you can use Superlinked to achieve quality retrieval, by implementing query time weights - at both query definition and query execution.

**Follow along in these Colabs.**
{% embed url="https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/query_time_weights.ipynb" %}
{% endembed %}

{% embed url="https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/dynamic_parameters.ipynb" %}
{% endembed %}

## Two ways to weight the query - definition

Our system lets you apply weights in two different ways:
1. **setting weights at query definition** - lets you experiment and optimize without re-embedding your dataset
2. **setting weights when running the query** - lets you (data scientist or user) fine-tune even after query definition

### Weighting when you define the query

Superlinked’s Spaces are structured for embedding different attributes of your data separately, permitting you to weight each attribute individually - before concatenating them into a single vector - when you define your queries. This enables you to run experiments, tuning the weights of different vector parts without having to re-embed your dataset.

Let’s walk through how you set this up in Superlinked, using an example where you define two queries - one that optimizes on paragraph similarity, and another that optimizes on like count.

After installing superlinked, you import the requisite modules: library, schema-related classes, index class, text_similarity and number spaces, query constructor, and display config (see cell 2). You then define your schema class and two spaces, and build an index on top of your spaces:

```python
@schema
class Paragraph:
    id: IdField
    body: String
    like_count: Integer

paragraph = Paragraph()

body_space = TextSimilaritySpace(
    text=paragraph.body, model="sentence-transformers/all-mpnet-base-v2"
)
like_space = NumberSpace(
    number=paragraph.like_count, min_value=0, max_value=100, mode=Mode.MAXIMUM
)
# indices can be built on top of multiple spaces as simply as:
paragraph_index = Index([body_space, like_space])
```

You create an in-memory data source and initialize it with the paragraph schema, initialize the in-memory executor, and add two paragraphs (your dataset), which are inserted into the source.

```python
source: InMemorySource = InMemorySource(paragraph)
executor = InMemoryExecutor(sources=[source], indices=[paragraph_index])
app = executor.run()


source.put(
    [
        {
            "id": "paragraph-1",
            "body": "Glorious animals live in the wilderness.",
            "like_count": 75,
        },
        {
            "id": "paragraph-2",
            "body": "Growing computation power enables advancements in AI.",
            "like_count": 10,
        },
    ]
)
```

Now that you have your system set up, you define your queries, a `body_query` that weights text similarity twice as much as likes, and another `like_query` that weights likes twice as much as text similarity.

```python
body_query = (
    Query(
        paragraph_index,
        weights={
            body_space: 1.0,
            like_space: 0.5,
        },
    )
    .find(paragraph)
    .similar(body_space.text, "What makes the AI industry go forward?")
)

like_query = (
    Query(
        paragraph_index,
        weights={
            body_space: 0.5,
            like_space: 1.0,
        },
    )
    .find(paragraph)
    .similar(body_space.text, "What makes the AI industry go forward?")
)
```

Running the `body_query` …
```python
body_result = app.query(body_query)

body_result.to_pandas()
```

…produces the following result:

|  | body | like_count | id |
|----|------|------------|-------|
| 0 | Growing computation power enables advancements in AI. | 10 | paragraph-2 |
| 1 | Glorious animals live in the wilderness. | 75 | paragraph-1 |



While running the `like_query` …
```python
like_result = app.query(like_query)

like_result.to_pandas()
```

ranks our results oppositely:

|  | body | like_count | id |
|----|------|------------|-------|
| 0 | Glorious animals live in the wilderness. | 75 | paragraph-1 |
| 1 | Growing computation power enables advancements in AI. | 10 | paragraph-2 |



By weighting when you define your query, you can set up searches that emphasize more relevant vector parts, without needing to re-embed your data.

But query definition is not the only opportunity to weigh different vector parts. In cases where you want to have more optimization power as a data scientist, or give your users more control over relevance, you can also set placeholder parameters when defining your queries that can be filled with weights when running the query.

### Weighting when you run the query - dynamic Params

In production systems, the developer generally defines the queries. The Superlinked approach gives you - the data scientist - the freedom to experiment with and fine-tune / optimize weights at query time - after the developer has defined the query. Or it gives the user more power to specify what’s more relevant to them. You set this up by putting placeholder Params in the query definitions - Params that you can fill in dynamically, weighting one or another parameter, when you run your query.

Using our example setup and data above, let’s look at how you can set weights when running the query.

As above, you import the requisite modules, but also import the Param class - which you’ll use to define dynamic parameters in queries (see cell 2 in the notebook). You then proceed with the set up as above (see cells 3-5).

Now that your have your system set up, you can define your queries using dynamic Param placeholders, so that they can be filled in later.

```python
query = (
    Query(
        paragraph_index,
        weights={
            body_space: Param("body_space_weight"),
            like_space: Param("like_space_weight"),
        },
    )
    .find(paragraph)
    .similar(body_space.text, Param("query_text"))
)
```

It’s time to query!
You now fill in your placeholder Params with weights, and generate results. To see how different query execution weights alter results, you run two queries. The first, `body_based_result`, queries by weighting the `body_space` at 1, and the `like_space` at 0, favoring the textually similar paragraph:

```python
body_based_result = app.query(
    query,
    query_text="How computation power changed the course of AI?",
    body_space_weight=1,
    like_space_weight=0,
)

body_based_result.to_pandas()
```



Your second query `like_based_result` reverses this weighting, and favors the most liked paragraph.

```python
like_based_result = app.query(
    query,
    query_text="How computation power changed the course of AI?",
    body_space_weight=0,
    like_space_weight=1,
)

like_based_result.to_pandas()
```





## In sum

Superlinked Spaces enable two different kinds of query time weighting, 1) weighting when defining the query, and 2) weighting when executing the query, each with its own associated benefits, and no need to rerank, build custom layers, or re-embed.
1. Because Superlinked permits you to assign weights when defining your queries, you can experiment and optimize without having to re-embed your dataset.
2. Assigning weights using dynamic parameters when you run the query offers the data scientist / user additional optimization control over what counts as relevant, even after query definition.


Now it’s your turn to run or experiment with the code in the notebooks: 
[Query time weights](https://github.com/superlinked/superlinked/blob/main/notebook/feature/query_time_weights.ipynb)
[Dynamic Paremeters](https://github.com/superlinked/superlinked/blob/main/notebook/feature/dynamic_parameters.ipynb)
Don’t forget to give us a star!