---
description: Superlinked through time.
icon: clock-rotate-left
---

# Changelog

## [9.22.1] - 2024-08-28

- #### Framework: v9.12.1 - v9.22.1
- #### Server: v9.12.1 - v9.22.0 (running with framework/v9.12.1)
- #### Batch: v1.1.0 - v1.1.2

### Added
- Event support in batch: Clients can now batch calculate with events as well, rendering the online and batch systems in feature parity.
- Support for more hard filter operations: Added support for LT, LTE, GT, GTE, AND, OR, CONTAINS, NOT_CONTAINS, IN, NOT_IN, unlocking more tabular data heavy use-cases.
- Optimized GPU usage: Optimized GPU utilization for best performance, which below a certain size (~10k embeddings) is more optimal with CPU.
- Integration tests of online executor with GPU: Added tests to measure if the frameworks correctly recognize the underlying GPU, if any.
- Added scores to example notebooks: Expanded all notebooks to show how scores work, allowing users to better understand the underlying vector similarity scores.
- Further NLQ support: Extended NLQ features with filter support and temperature tuning based on feedback.

### Fixed
- Results were not ordered by score with Redis: Fixed issue where results were not properly ordered by their scores in ascending order.
- Long categorical embeddings were dominating the results: Fixed an issue that resulted in all 0 vectors that skewed the results by breaking the normalization.
- Source.put was behaving differently with different inputs: Fixed to work as expected with arrays and data frames alike.
- Index temperature was not accepting integers: Fixed the index to accept integer temperatures.

### Changed
- Added better formatted logs in tests: Improved logging support for easier issue identification during development.
- (breaking) Removed status endpoints for initial data loader: Necessary step to allow the executor to be stateless, preparing it for high availability hosting.

### Misc
- Benchmarked the batch performance: Ran batch in GCP for the first time and benchmarked the performance (700k items under 4 mins).

## [9.12.1] - 2024-08-14

- #### Framework: v9.7.0 - v9.12.1
- #### Server: v9.6.0 - v9.7.0 (running with v9.2.0)
- #### Batch: v1.0.2 - v1.1.0

### Added
- Return similarity scores: Now returning similarity scores along with results, allowing clients to better understand the distribution.
- Improved feature notebooks: Extended with examples containing similarity scores, querying of recency space, and event parameters (max_count, max_age, temperature).
- Code quality checks for server: Added automations to ensure server testing and unified code format.

### Fixed
- Recency was not always using the same NOW from the context: Fixed to use the correct reference point.

### Changed
- Conducted retrospective meetings for Natural Language Queries and Distributing Superlinked Batch.


## [9.7.0] - 2024-08-07

- #### Framework: v9.7.0
- #### Server: v9.6.0
- #### Batch: v1.0.2

### Added
- Bumped sentence-transformers to 3.0.1: Allows experimentation with highest scoring models from mteb leaderboard.
- Support for empty list embedding: Enables ingestion of data with lists where not all rows have an item.
- Default limits to vector database connectors: Set default return of 10 items for both Redis and Mongo.
- Natural Language Queries: Users can describe parameters for prompting the underlying model.
- Support logarithmic number embeddings: Captures non-linear preferences with large values.

### Fixed
- Negative weights boosting recommendations: Fixed issues within the event handling system.
- Negative weight now applied even for the first received event: Addressed bug where negative weights only worked after a positively weighted event.