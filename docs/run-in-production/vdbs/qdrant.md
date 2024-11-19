# Qdrant

This document provides clear steps on how to use and integrate Qdrant with Superlinked.

## Configuring your existing managed Qdrant

To use Superlinked with Qdrant, start a managed instance provided by Qdrant (a free-tier is available). For detailed steps on initializing a managed instance, refer to the [Start a Managed Qdrant Instance](#start-a-managed-qdrant-instance) section below.

Once your Qdrant instance is up and running, ensure it is accessible from the server that will use it. Additionally, configure the necessary authentication settings as described below.

## Modifications in your configuration

To integrate Qdrant, you need to add the `QdrantVectorDatabase` class and include it in the executor. Here’s how you can do it:
```python
from superlinked.framework import QdrantVectorDatabase

vector_database = QdrantVectorDatabase(
    "<your_qdrant_url>", # (Mandatory) This is your qdrant URL generally with a port but without any extra fields
    "<your_api_key>", # (Mandatory) This is the api key to your qdrant cluster
    # The following params must be in a form of kwarg params. Here you can specify anything that the official python client enables. For more details visit:
    # https://python-client.qdrant.tech/qdrant_client.qdrant_client.
    default_query_limit=10, # This optional parameter specifies the maximum number of query results returned. If not set, it defaults to 10.
)
```

Once you have configured the vector database just simply pass it to the executor.
```python
...
executor = RestExecutor(
    sources=[source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=vector_database,
)
...
```

## Start a Managed Qdrant Instance

To initialize a managed Qdrant instance, navigate to [Qdrant](https://cloud.qdrant.io/login), sign in then click on "Overview" on the left side of the page. Here, you can create a free-tier or production-ready clusters. A free-tier offers 0.5 vCPU, 1GB memory, 4GB disk space running on 1 node. You can customize these parameters with a paid plan. You can also choose your prefered platform, location and whether high-availability (HA) is a necessity.
After the cluster was created, generate an API key and save it to a secure place, you won't be able to see it again. This key is part of the QdrantVectorDatabase configuration.

## Example app with Qdrant

You can find an example that utilizes Qdrant [here](https://github.com/superlinked/superlinked/blob/main/docs/run-in-production/vdbs/qdrant/app_with_qdrant.py).
