---
description: Explore the core ideas and principles behind Superlinked's functionality..
icon: bullseye-arrow
---

# Overview


1. Describe your data using Python classes with the [@schema](../reference/common/schema/schema.md) decorator.
2. Describe your vector embeddings from building blocks with [Spaces](../reference/dsl/space/index.md).
3. Combine your embeddings into a queryable [Index](../reference/dsl/index/index.md).
4. Define your search with dynamic parameters and weights as a [Query](../reference/dsl/query/query.md).
5. Load your data using a [Source](../reference/dsl/source/index.md).
6. Define your transformations with a [Parser](../reference/common/parser) (e.g.: from [`pd.DataFrame`](../reference/common/parser/dataframe_parser.md)). 
7. Run your configuration with an [Executor](../reference/dsl/executor/in_memory/in_memory_executor.md).


## Colab notebooks explaining the concepts

<table data-view="cards">
<thead>
<tr><th></th><th></th><th data-type="content-ref"></th><th data-hidden data-card-cover data-type="files"></th><th data-hidden data-card-target data-type="content-ref">
</th></tr>
</thead>
<tbody>
    <tr>
        <td><strong>Categorical Embeddings</strong></td>
        <td>Efficiently represent and compare categorical data in vector space for similarity searches.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Categorical Embeddings.png">Categorical Embeddings.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/categorical_embedding.ipynb" target="_blank">categorical_embeddings</a></td>
    </tr>
    <tr>
        <td><strong>Combine Multiple Embeddings</strong></td>
        <td>Merge different types of embeddings to create a unified representation for complex objects.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Combine Multiple Embeddings.png">Combine Multiple Embeddings.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/combine_multiple_embeddings.ipynb" target="_blank">combine_multiple_embeddings</a></td>
    </tr>
    <tr>
        <td><strong>Custom Spaces</strong></td>
        <td>Create and manage custom vector spaces for specialized similarity searches.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Custom Spaces.png">Custom Spaces.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/custom_space.ipynb" target="_blank">custom_spaces</a></td>
    </tr>
    <tr>
        <td><strong>Dynamic Parameters</strong></td>
        <td>Adjust query parameters dynamically to fine-tune search results.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Dynamic Parameters.png">Dynamic Parameters.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/dynamic_parameters.ipynb" target="_blank">dynamic_parameters</a></td>
    </tr>
    <tr>
        <td><strong>Event Effects</strong></td>
        <td>Model and apply the impact of events on vector representations over time.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Event Effects.png">Event Effects.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/event_effects.ipynb" target="_blank">event_effects</a></td>
    </tr>
    <tr>
        <td><strong>Hard Filtering</strong></td>
        <td>Apply strict criteria to narrow down search results before similarity ranking.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Hard Filtering.png">Hard Filtering.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/hard_filtering.ipynb" target="_blank">hard_filtering</a></td>
    </tr>
    <tr>
        <td><strong>Natural Language Querying</strong></td>
        <td>Perform similarity searches using natural language queries instead of vector representations.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Natural Language Querying.png">Natural Language Querying.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/natural_language_querying.ipynb" target="_blank">natural_language_querying</a></td>
    </tr>
    <tr>
        <td><strong>Number Embedding Minmax</strong></td>
        <td>Embed numerical values within a specified range for effective similarity comparisons.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Number Embedding Minmax.png">Number Embedding Minmax.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/number_embedding_minmax.ipynb" target="_blank">number_embedding_minmax</a></td>
    </tr>
    <tr>
        <td><strong>Number Embedding Similar</strong></td>
        <td>Embed numbers to find similar values based on relative closeness rather than exact matches.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Number Embedding Similar.png">Number Embedding Similar.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/number_embedding_similar.ipynb" target="_blank">number_embedding_similar</a></td>
    </tr>
    <tr>
        <td><strong>Query by Object</strong></td>
        <td>Search for similar items using an existing object as the query input.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Query by Object.png">Query by Object.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/query_by_object.ipynb" target="_blank">query_by_object</a></td>
    </tr>
    <tr>
        <td><strong>Query Time Weights</strong></td>
        <td>Adjust the importance of different embedding components during query execution.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Query Time Weights.png">Query Time Weights.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/query_time_weights.ipynb" target="_blank">query_time_weights</a></td>
    </tr>
    <tr>
        <td><strong>Querying Options</strong></td>
        <td>Customize search behavior with various querying options for refined results.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Querying Options.png">Querying Options.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/querying_options.ipynb" target="_blank">querying_options</a></td>
    </tr>
    <tr>
        <td><strong>Recency Embedding</strong></td>
        <td>Incorporate time-based relevance into vector representations for up-to-date search results.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Recency Embedding.png">Recency Embedding.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/recency_embedding.ipynb" target="_blank">recency_embedding</a></td>
    </tr>
    <tr>
        <td><strong>Text Embedding</strong></td>
        <td>Convert text data into vector representations for semantic similarity searches.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Text Embedding.png">Text Embedding.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/text_embedding.ipynb" target="_blank">text_embedding</a></td>
    </tr>
    <tr>
        <td><strong>Vector Sampler</strong></td>
        <td>Generate diverse vector samples to explore and understand the embedding space.</td>
        <td></td>
        <td><a href="../.gitbook/assets/concept-thumbnails/Vector Sampling.png">Vector Sampling.png</a></td>
        <td><a href="https://github.com/superlinked/superlinked/blob/main/notebook/feature/vector_sampler.ipynb" target="_blank">vector_sampler</a></td>
    </tr>

    
</tbody>
</table>