# Using the API to ingest and query the application

Once you have your application up and running, you can start loading data and querying the API. Here's a step-by-step guide on how to do it:

## Ingest an entry

1. **Data Ingestion**: You can test data ingestion by making a POST request to the `/api/v1/ingest/your_schema` endpoint. Here's an example using `curl`:
    ```bash
    curl -X POST \
        'http://localhost:8080/api/v1/ingest/your_schema' \
        --header 'Accept: */*' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "id": "your_id",
            ...
        }'
    ```
    > **Note**: The current example will not work, please change the request body as your schema requires it.

## Query your system

1. **Query the API**: After ingesting data, you can query the API by making a POST request to the `/api/v1/search/query` endpoint. Here's an example using `curl`:
    ```bash
    curl -X POST \
        'http://localhost:8080/api/v1/search/query' \
        --header 'Accept: */*' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "query_text": "your_search_text"
        }'
    ```
This request will search for entities that match the query text.

## Load data from file(s)

### Trigger the data load

To initiate the data load, invoke it's endpoint. This will spawn one asynchronous task for each `DataLoaderSource` that you defined in your `app.py`. To trigger the endpoint, simply send a request with `curl` shown below. The response should be 202 Accepted and it will contain the task id(s).

```bash
curl -X POST 'http://localhost:8080/data-loader/run'
```
Successful response (200 OK):
```JSON
{
    "result": "Background task(s) successfully started. For status, check: `/data-loader/<task_id>`",
    "task_ids": ["<TASK_ID>", "<TASK_ID>"]
}
```

> Note: Ensure not to run two data loaders concurrently. The latter one will overwrite the already persisted data.

### See the status of your tasks

To check if your data is still loaded to the system, you can trigger the status endpoint. The endpoint needs a task id, that you previously got when invoked the data load endpoint. If you have multiple of them, you need to send one request for each task. The endpoint will return with 200s if the given task id exists in the system and 404 if not. The response will be a JSON with a human readable reasoning what happened. If it failed, you still get a 200 with the reasoning in the body.

```bash
curl -X GET 'http://localhost:8080/data-loader/<TASK_ID>/status
```
Successful response (200 OK):
```JSON
{
    "result": "Task is still running",
}
```
If the task id not found in the system (404 Not found):
```JSON
{
    "result": "Task not found with id: <TASK_ID>",
}
```
