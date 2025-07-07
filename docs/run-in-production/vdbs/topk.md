# TopK

This document provides clear steps on how to use and integrate TopK with Superlinked.

## Configuring your existing TopK account

To use Superlinked with TopK, you'll need to create a TopK account and set up a project. For detailed steps on setting up your TopK account, refer to the [Set up your TopK Account](#set-up-your-topk-account) section below.

Once your TopK project is set up, you'll need to obtain your API key and region information to configure the authentication settings as described below.

## Modifications in your configuration

To integrate TopK, you need to add the `TopKVectorDatabase` class and include it in the executor. Here’s how you can do it:

````python
from superlinked import framework as sl

vector_database = sl.TopKVectorDatabase(
    api_key="<your_api_key>", # (Mandatory) This is your TopK API key
    region="<your_region>", # (Mandatory) This is your TopK region
    default_query_limit=10, # (Optional) This parameter specifies the maximum number of query results returned. If not set, it defaults to 10.
)

Once you have configured the vector database just simply pass it to the executor.

```python
...
executor = sl.RestExecutor(
    sources=[source],
    indices=[index],
    queries=[sl.RestQuery(sl.RestDescriptor("query"), query)],
    vector_database=vector_database,
)
...
````

## Set up your TopK Account

To set up your TopK account and obtain the necessary credentials for Superlinked integration, follow these steps:

1. **Go to the TopK Console**
   Navigate to [TopK Console](https://console.topk.io) and create an account or sign in to your existing account.

2. **Create or Select a Project**
   TopK follows an `Organization > Project > Collection` hierarchical structure. Create a new project or use an existing one within your organization.

3. **Generate an API Key**
   Follow the TopK [documentation](https://docs.topk.io/installation#api-key) to generate a API key for your project.

4. **Note your Region**
   TopK is region-specific. Refer to the TopK documentation for available regions and ensure you use the correct region for your project. Attempting to access collections or documents outside the specified region will result in a region mismatch error.

## Example app with TopK

You can find an example that utilizes TopK [here](https://github.com/superlinked/superlinked/blob/main/docs/run-in-production/vdbs/topk/app_with_topk.py).
