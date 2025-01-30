---
description: How Superlinked represents your complex data better.
icon: table
---

# Combining multiple embeddings to represent complex data better

Getting quality retrieval results from LLM queries on embedded complex data is no walk in the park. The typical approach looks something like this, and has serious shortcomings:
1. embed all the data you have about an entity as a single piece of text (using a model from a hub like Hugging Face, or your own proprietary model).

{% hint style="info" %}
Converting all the data you have about an entity directly into a single vector usually fails to capture complex attributes; you lose potentially relevant information.
{% endhint %}


2. run a vector search to identify X nearest neighbor vectors in order.

{% hint style="info" %}
Similarity searches on these vectors often produce less than satisfactory results, necessitating reranking.
{% endhint %}


3. rerank your results using a) additional contextual filters or b) information not in the vector (e.g., filtering out items that are out of stock)

{% hint style="info" %}
To get better results, you’ll probably have to add a custom layer to incorporate additional relevant information, and/or rerank using cross-encoders, incurring a latency cost that threatens productionizing; cross-encoders obtain a reranking metric by calculating the similarity of each pair of points individually, which takes a nontrivial amount of time.
{% endhint %}


Is there a way of achieving quality retrieval without the data loss and latency cost of the typical approach (above)? **Yes!**

Instead of embedding all the data you have about an entity as a single vector, you can use Superlinked Spaces to embed it as different modalities, one vector per modality, and concatenate those vectors into a multimodal vector. By capturing the full complexity of your data, you can achieve better quality search results without having to add an additional layer or reranking.

To illustrate the Superlinked approach, let’s take a look at a simple example.

**Follow along in this Colab.**
{% embed url="https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/feature/combine_multiple_embeddings.ipynb" %}
{% endembed %}

## A more efficient, reliable approach to complex search

The pieces of information you have about any entity are often complex and usually include more than one attribute. Let’s take a very simple example. Say your data source contains two paragraphs, each with a certain number of likes:
1. “Glorious animals live in the wilderness." like_count = 10
2. "Growing computation power enables advancements in AI." like_count = 75

Each of the paragraph data’s modalities (i.e., the paragraph text and the like_count) can be captured individually in separate embeddings and then concatenated into a single multimodal vector that better represents the original data.

By combining this complex structured and unstructured data about each entity into a single vector in your vector index, you take advantage of the power your vector database, which is optimized for vector search. As a result, you can achieve:
- **better quality retrieval results:** your searches can retrieve results that are more complete and relevant than when your embeddings did not effectively represent different attributes of the same entity; see Superlinked’s research outcomes on this in VectorHub:
  - [Combining semantic embeddings with graph embeddings to improve the performance of LLMs on relational data](https://superlinked.com/vectorhub/articles/answering-questions-knowledge-graph-embeddings)
  - [Combining multimodal text and image embeddings using aligned encoders to increase retrieval performance](https://superlinked.com/vectorhub/articles/retrieval-from-image-text-modalities)
- **efficiency savings:** because you get better results, you’re less likely to require time-consuming reranking, thereby reducing the processing time for vector retrieval by a factor of 10 (instead of hundreds of milliseconds, your retrieval takes only 10s of milliseconds)

But how do we both represent all the complex attributes of a given entity and combine them into a single vector that’s easily searchable in a vector index? 
Superlinked handles this with Spaces.

## Capturing complex entity data in a single multimodal vector - Superlinked’s Spaces

At Superlinked, we use Spaces to embed different pieces of data, structured or unstructured, about an entity and concatenate them into a single, representative multimodal vector that’s easy to query in your vector index. Our Spaces approach achieves better retrieval by carefully building more representative vectors before you start retrieving - as opposed to embedding all the data you have about an entity as a single piece of text inadequately capturing all the varied attributes of the entity, and then having to rerank and filter to incorporate or omit other attributes. Spaces lets you foreground the most relevant attributes of your data when embedding.

Instead of converting your data about, for example, users or products directly into a single vector, Superlinked’s approach lets you represent different attributes about the same entity in separate Spaces, each of which handles that type of data better. One Space handles data about attribute x from users and another Space captures data about attribute y from users, etc., and the same for products.

But Spaces also enables you to combine data from more than one schema in the same Space. You can, for example, declare one Space that represents related attributes of data from both users and the products - e.g., product description and user product preferences. Once you’ve used a Space to connect user preference data with product descriptions in your embeddings, searching with the user preference vector will surface better product recommendations.

Let’s see what this looks like in terms of code. 

Once you’ve defined your data types in `@schema`, you embed your data using Spaces that are appropriate to your data types. For example, category information uses the `CategoricalSimilaritySpace`, and text uses the `TextSimilaritySpace`.

Using our simple two-paragraph dataset above, we proceed as follows:

```python
@sl.schema
class Paragraph:
    id: sl.IdField
    body: sl.String
    like_count: sl.Integer
```

Once you’ve defined your data types using `@sl.schema`, you embed these using Spaces that fit your data types:

```python
body_space = sl.TextSimilaritySpace(
    text=paragraph.body, model="sentence-transformers/all-mpnet-base-v2"
)
like_space = sl.NumberSpace(
    number=paragraph.like_count, min_value=0, max_value=100, mode=sl.Mode.MAXIMUM
)
```

These Spaces can now be combined into a single index.

```python
paragraph_index = sl.Index([body_space, like_space])
```
…and queried. 

```python
query = (
    sl.Query(paragraph_index).find(paragraph).similar(body_space.text, sl.Param("query_text")).select_all()
)
result = app.query(
    query,
    query_text="What makes the AI industry go forward?",
)
```
Here, we query our index to search for the most similar `body_space`, and surface our results in the appropriate order:

|  | body | like_count | id |
|----|------|------------|-------|
| 0 | Growing computation power enables advancements in AI. | 75 | paragraph-2 |
| 1 | Glorious animals live in the wilderness. | 10 | paragraph-1 |




## Wrapping up…

Above, we lay bare the basics of how Superlinked’s Spaces make it very straightforward and simple to improve retrieval quality and efficiency - by embedding all the complex attributes of your data in multiple embeddings, and combining them in a single queryable index.


Our example above is extremely simple; the Superlinked system is built to handle all kinds of far more complex data sources and use cases, producing accurate, relevant outcomes, without time- and resource-costly additional layers and reranking.


Check out the [notebook](https://github.com/superlinked/superlinked/blob/main/notebook/feature/combine_multiple_embeddings.ipynb) for more details on how to combine multiple embeddings for better retrieval. Don’t forget to give us a star!