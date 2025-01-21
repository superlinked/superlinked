---
icon: hotel
---

# Hotel Search

## Overview

This project is a demonstration of a hotel search system built using Superlinked.
It allows users to search for hotels based on various criteria such as description, price, rating, and more, all through natural language queries.

{% hint style="info" %}
🚀 Try it out: [hotel-search-recipe.superlinked.io](https://hotel-search-recipe.superlinked.io/)
{% endhint %}

{% hint style="info" %}
💻 Github repo: [here](https://github.com/superlinked/superlinked-recipes/tree/main/projects/hotel-search)
{% endhint %}



### Key Features:
- **Natural Language Queries:** Search for hotels using everyday language.
- **Multi-modal Semantic Search:** Utilize different data types for comprehensive search results.

### Query examples:
- Cheap but highly rated hotels in Paris, no children
- No pets, posh hotel in Berlin
- Popular hotels in center of London with free breakfast

### Modalities:
- **Text:** Hotel descriptions.
- **Numbers:** Price, rating, and number of reviews.

### Hard-filters:
- **Location:** City.
- **Numbers:** Price, ratings.
- **Amenities:** Options for property and room amenities; 
  wellnes and spa; accessibility; children.

### Data example (hotel entity):

```json
{
    "id": "Lovely Hotel",
    "country": "Germany",
    "city": "Berlin",
    "accomodation_type": "Hotel",
    "price": 42,
    "image_src": "...",
    "description": "A family hotel close to city center ...",
    "rating_count": 6543,
    "rating": 8.9,
    "property_amenities": ["Free parking", "Breakfast"],
    "room_amenities": ["Air conditioning", "Balcony"],
    "wellness_spa": [],
    "accessibility": ["Wheelchair accessible"],
    "for_children": ["Childcare", "Cot"],
}
```
### How it works in a nutshell

<div align="center">
  <img src="./assets/superlinked-in-a-nutshell.svg" alt="Superlinked in a nutshell">
</div>

## Quick Start

This section provides a step-by-step guide on how to run the whole system locally.

More details are provided below, in the **Tutorial** section.

<div align="center">
  <img src="./assets/architecture.svg" alt="System Architecture" width="50%">
</div>

### Redis VDB

```shell
docker run -d \
  --name redis-vdb-hotel-search \
  -p 6379:6379 \
  -p 8001:8001 \
  -v "$(pwd)"/redis-data:/data \
  -e REDIS_ARGS="--appendonly yes --appendfsync everysec" \
  -e REDISINSIGHT_HOST=0.0.0.0 \
  redis/redis-stack:7.4.0-v0
```

Once running, you can access the Redis browser at [localhost:8001/browser](http://localhost:8001/browser/).

For more details on using Redis with Superlinked, refer to the [our docs](https://docs.superlinked.com/run-in-production/index-1/redis).

### Superlinked server

Use [`superlinked_app/.env-example`](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/.env-example) as a template, create `superlinked_app/.env` and set `OPENAI_API_KEY` required for Natural Query Interface.

```shell
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
APP_MODULE_PATH=superlinked_app python -m superlinked.server
```

It will take some time (depending on the network) to download the sentence-transformers model for the very first time.

API docs will be available at [localhost:8080/docs](http://localhost:8080/docs).

To ingest the dataset, run this command in your terminal:
```shell
curl -X 'POST' \
  'http://localhost:8080/data-loader/hotel/run' \
  -H 'accept: application/json' \
  -d ''
```

### Streamlit frontend

```shell
cd frontend_app
python3.11 -m venv .venv-frontend
. .venv-frontend/bin/activate
pip install -e .
python -m streamlit run app/frontend/main.py
```

The Streamlit UI will be available at [localhost:8501](http://localhost:8501).

### Jupyter notebook

Attach to VDB and experiment with different superlinked queries from the jupyter notebook: [superlinked-queries.ipynb](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/notebooks/superlinked-queries.ipynb).

## Cloud

The `superlinked cli` is a one-package solution to deploy the Superlinked cluster on your GCP cloud.
Via `superlinked cli` you will be able to run superlinked application at scale with additional important components such as batch engine, logging and more, utilizing the same superlinked configuration you used in your local setup!

Want to try it now? Contact us at [superlinked.com](https://superlinked.typeform.com/to/LXMRzHWk?typeform-source=hotel-search-recipe).

## Tutorial

To configure your superlinked application you need to create a simple python package with few files, we will go though them one by one.
All files contain necessary inline comments, check them out!
Also, feel free to read our docs: [docs.superlinked.com](https://docs.superlinked.com/run-in-production/index/configuring-your-app).

Once you are happy with your local Superlinked setup, you can use config files without changes for your Cloud deployent.
To make transition to the cloud smooth, we provide Superlinked CLI.
[Contact us](https://superlinked.typeform.com/to/LXMRzHWk?typeform-source=hotel-search-recipe) if you want to try it now!

---

[**`__init__.py`**](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/__init__.py)

It's needed just to make a python package, you can keep it empty.

---

[**`config.py`**](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/config.py)

Settings of our application are read from `.env` file.
You can create one simply by copying [`.env-example`](./superlinked_app/.env-example) and setting `openai_api_key` which is needed for NLQ.

---

[**`index.py`**](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/index.py)

This file defines three important things:
- object schema: declares names and types of raw attributes
- vector spaces: bind embedders to schema fields
- index: combines spaces for multi-modal vector search

<div align="center">
  <img src="./assets/superlinked-index.svg" alt="Graphical abstract">
</div>

In our superlinked application, we will embed one textual field (hotel `description`) and three numeric fields (`price`, `rating`, `rating_count`).
Description is embedded using [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2).
If you need faster model, you can try [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
Or if you are aiming for better retrieval quality, bigger models like [gte-large-en-v1.5](https://huggingface.co/Alibaba-NLP/gte-large-en-v1.5) are worth checking out.

**Note.** Apart from texts and numbers, out-of-the-box Superlinked can embed images, categories, recency.
It also supports arbitrary embeddings via custom spaces.
Learn more about Superlinked embeddings in [our github](https://github.com/superlinked/superlinked/tree/main?tab=readme-ov-file#features)!

Attribues like city, hotel-type, and amenities are used for hard-filtering.

---

[**`query.py`**](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/query.py) and [**`nlq.py`**](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/nlq.py)

These two files define superlinked queries used for multi-modal semantic search with Natural Language Interface (NLI) on top.
Our github contains many helpful notebooks that show how to configure superlinked queries:
- [query time weights](https://github.com/superlinked/superlinked/blob/main/notebook/feature/query_time_weights.ipynb)
- [querying options](https://github.com/superlinked/superlinked/blob/main/notebook/feature/querying_options.ipynb)
- [dynamic parameters](https://github.com/superlinked/superlinked/blob/main/notebook/feature/dynamic_parameters.ipynb)
- [natural language interface](https://github.com/superlinked/superlinked/blob/main/notebook/feature/natural_language_querying.ipynb)

---

[**`api.py`**](https://github.com/superlinked/superlinked-recipes/blob/main/projects/hotel-search/superlinked_app/api.py)

This file sets the following components:
- vector database: in current application we are using Redis.
  We also support [MongoDB and Qdrant](https://docs.superlinked.com/run-in-production/index-1).
- data loader: our data is ingested from gcp bucket
- REST API: our app will provide endpoints for ingestion (bulk and one-by-one) and for querying. More information is in [our docs](https://docs.superlinked.com/run-in-production/index/interacting-with-app-via-api).

## What's next

We publish our recipes as a starting point for your own projects.
There are many things you might want to try:
- **Experiment with superlinked queries.**
  Try to come up with more queries focused on different search scenarios fitting your use-case.
- **Bring your own dataset.**
  Want to run Natural Language Query with your data?
  Define your schema, spaces, index, queries, and data-sources based on this recipe.
  In case of questions, don't hesitate to [contact us](https://superlinked.typeform.com/to/LXMRzHWk?typeform-source=hotel-search-recipe)!
- **Try different VDBs.**
  Depending on your needs you can choose one of the [VDBs we currently support](https://docs.superlinked.com/run-in-production/index-1).
  More to come!
- **Try other text embedding models.**
  There are a ton of different text embedding models out there.
  Discover [sentence-transformers](https://sbert.net/docs/sentence_transformer/pretrained_models.html), [hugging-face](https://huggingface.co/sentence-transformers) and select models that suit your use-case best.
- **Explore additional use-cases.** Check out our [notebooks](https://github.com/superlinked/superlinked/tree/main/notebook) and [docs](https://docs.superlinked.com/).