---
description: Superlinked through time.
icon: clock-rotate-left
---

# Changelog

## [9.43.0] - 2024-09-25

- #### Framework: v9.33.0 - v9.43.0
- #### Server: v9.33.0 - v9.42.1 (running with framework/v9.42.1)
- #### Batch: v1.4.0 - v1.8.0

### Added
- **NLQ support for IN and NOT_IN operators**: Added support for NLQ to translate natural language to IN and NOT_IN operators.
- **Logging for superlinked components**: Logging was added for unified debugging and observability, led by Krisztian.
- **Basic caching for text-embeddings**: Implemented caching for 10k items to handle repeating inputs efficiently.


### Fixed
- **Chunking with hard-filters**: Fixed an issue where chunking was breaking hard-filters.
- **Limit NLQ to respect given categories**: Ensured NLQ does not "hallucinate" categories not present in the application.

### Changed
- **Image embedding model update**: Replaced the image embedding model in the use-case notebook with the latest model.

### Misc
- **Batch infrastructure risk mitigation**: Verified that the GCP hosted solution works as intended.
- **Hard-filter compatibility with batch**: Ensured compatibility of IN, NOT_IN, LT, LTE, GT, GTE operators with batch-encoded datasets.


## [9.33.0] - 2024-09-11

- #### Framework: v9.22.1 - v9.33.0
- #### Server: v9.33.0 - v9.33.0 (running with framework/v9.33.0)
- #### Batch: v1.1.2 - v1.4.0

### Added
- **Separated the user code into multiple files**: We have separated the previous app.py into dedicated index.py/query.py/api.py, which promotes reusability and explainability of the system behavior.
- **Added “or” and “contains” to the notebooks**: Added further examples to notebooks based on user feedback.

### Fixed
- **Fixed skewed vectors, when recency was 0**: A known limitation of the system is that, if full zero vectors make it to the index or query as an output of a space, then the weighting logic.
- **Added NLQ support for in and not_in operators**: Newly introduced hard-filters were not properly handled by NLQ before.
- **Fixed hard-filters with chunking**: Hard-filters were not tested with chunking, this is now fixed.

### Changed
- **Improved the system message at server startup**: Users were experiencing confusing when starting up server as the messages were not clear on the status.



## [9.22.1] - 2024-08-28

- #### Framework: v9.12.1 - v9.22.1
- #### Server: v9.12.1 - v9.22.0 (running with framework/v9.12.1)
- #### Batch: v1.1.0 - v1.1.2

### Added
- **Event support in batch**: Users can now batch calculate with events as well, rendering the online and batch systems in feature parity.
- **Support for more hard filter operations**: Added support for LT, LTE, GT, GTE, AND, OR, CONTAINS, NOT_CONTAINS, IN, NOT_IN, unlocking more tabular data heavy use-cases.
- **Optimized GPU usage**: Optimized GPU utilization for best performance, which below a certain size (~10k embeddings) is more optimal with CPU.
- **Integration tests of online executor with GPU**: Added tests to measure if the frameworks correctly recognize the underlying GPU, if any.
- **Added scores to example notebooks**: Expanded all notebooks to show how scores work, allowing users to better understand the underlying vector similarity scores.
- **Further NLQ support**: Extended NLQ features with filter support and temperature tuning based on feedback.

### Fixed
- **Results were not ordered by score with Redis**: Fixed issue where results were not properly ordered by their scores in ascending order.
- **Long categorical embeddings were dominating the results**: Fixed an issue that resulted in all 0 vectors that skewed the results by breaking the normalization.
- **Source.put was behaving differently with different inputs**: Fixed to work as expected with arrays and data frames alike.
- **Index temperature was not accepting integers**: Fixed the index to accept integer temperatures.

### Changed
- **Added better formatted logs in tests**: Improved logging support for easier issue identification during development.
- **(breaking) Removed status endpoints for initial data loader**: Necessary step to allow the executor to be stateless, preparing it for high availability hosting.

  

## [9.12.1] - 2024-08-14

- #### Framework: v9.7.0 - v9.12.1
- #### Server: v9.6.0 - v9.7.0 (running with v9.2.0)
- #### Batch: v1.0.2 - v1.1.0

### Added
- **Return similarity scores**: Now returning similarity scores along with results, allowing clients to better understand the distribution.
- **Improved feature notebooks**: Extended with examples containing similarity scores, querying of recency space, and event parameters (max_count, max_age, temperature).
- **Code quality checks for server**: Added automations to ensure server testing and unified code format.

### Fixed
- **Recency was not always using the same NOW from the context**: Fixed to use the correct reference point.



## [9.7.0] - 2024-08-07

- #### Framework: v9.7.0
- #### Server: v9.6.0
- #### Batch: v1.0.2

### Added
- **Bumped sentence-transformers to 3.0.1**: Allows experimentation with highest scoring models from mteb leaderboard.
- **Support for empty list embedding**: Enables ingestion of data with lists where not all rows have an item.
- **Default limits to vector database connectors**: Set default return of 10 items for both Redis and Mongo.
- **Natural Language Queries**: Users can describe parameters for prompting the underlying model.
- **Support logarithmic number embeddings**: Captures non-linear preferences with large values.

### Fixed
- **Negative weights boosting recommendations**: Fixed issues within the event handling system.
- **Negative weight now applied even for the first received event**: Addressed bug where negative weights only worked after a positively weighted event.