# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [33.3.0] - 2025-08-04

### Added

- Add persistence support for image embedding nodes for events

## [33.0.0] - 2025-07-30

### Added

- Add entity cache to online recency node's get_fallback_results

### Changed

- Revert python version change

### Fixed

- Handle default number/recency node for ingestion -> zero vector like others
- Fix wrong merge conflict resolution

## [32.4.0] - 2025-07-29

### Changed

- Make ConcatenationNode persistence configurable based on effects

## [32.3.0] - 2025-07-28

### Changed

- Rename ValidationException to InvalidInputException

## [32.2.1] - 2025-07-28

### Fixed

- Blob loader works on nullable input

## [32.2.0] - 2025-07-23

### Changed

- Introduce fallback logic in online entity cache

### Removed

- Remove loading cache on item ingestion

## [32.1.0] - 2025-07-23

### Added

- Add TODOs (FAB-3639)

### Changed

- Restructured EntityDataRequest
- Node info
- New cache
- Move persistable_nodes to OnlineSchemaDag
- Online dag evaluator with new requests
- Load node info
- Handle origin ids
- Group event related cache operations
- Frozen node requests
- Split calculate field by delta or merge

### Fixed

- Turn method into property - online entity cache

### Removed

- Remove usage of old cache
- Remove legacy EntityDataRequest
- Remove iterator
- Remove leftover

## [32.0.0] - 2025-07-22

### Removed

- Remove new dict creation

## [31.4.1] - 2025-07-21

### Changed

- Return the query and source with the paths
- Improve modal image build time

## [31.4.0] - 2025-07-21

### Changed

- Jira issue notebook

## [31.3.0] - 2025-07-21

### Changed

- Enable passing nested settings as os vars

## [31.2.4] - 2025-07-21

### Fixed

- Moved rich dependency from dev to amin deps, to avoid recursion error

## [31.2.3] - 2025-07-18

### Fixed

- Fix ref urls in change notes

## [31.2.2] - 2025-07-18

### Fixed

- Proper diff handling in change notes

## [31.2.1] - 2025-07-18

### Fixed

- Increase Redis max connections to 170 for improved throughput

## [31.2.0] - 2025-07-18

### Changed

- Reduce Redis max connections from 200 to 150

### Fixed

- Include CHANGELOG.md in build examples and adjust Redis connection pool

## [31.1.0] - 2025-07-18

### Changed

- Implement in-memory caching for online DAG evaluation
- Improve schema reference handling in DAG evaluator

## [30.2.0] - 2025-07-17

### Added

- Add MODEL_WARMUP configuration option for embedding models

## [30.1.0] - 2025-07-17

### Removed

- Remove Hugging Face API-based embedding support

## [30.0.0] - 2025-07-15

### Added

- Add detailed metrics and spans

### Fixed

- Copy paste error

## [29.6.5] - 2025-07-11

### Changed

- Disable progress bar in SentenceTransformers encoding
- Reduce connection pool size and increase timeout
- Handle missing fields gracefully in search results

## [29.6.4] - 2025-07-10

### Added

- Add FilterPredicate
- Add aggregation.filter_predicate

### Changed

- Custom filter predicates
- Adjust thresholds

### Fixed

- Cap rich version to prevent recursion error

### Removed

- Remove is not on floats in aggregation

## [29.6.2] - 2025-07-09

### Removed

- Remove unnecessary connection refresh mechanism

## [29.6.1] - 2025-07-09

### Removed

- Remove execution profiling system and improve singleton handling to allow pickling

## [29.6.0] - 2025-07-08

### Fixed

- Ease auto import of settings

## [29.5.0] - 2025-07-08

### Changed

- Use initialized settings

### Removed

- Remove leftover

## [29.4.0] - 2025-07-08

### Added

- Add VersionResolver

## [29.3.0] - 2025-07-08

### Removed

- Remove singleton from settings

## [29.2.1] - 2025-07-07

### Changed

- Expand comment explaining effect grouping race conditions

## [29.1.0] - 2025-07-03

### Added

- Add span processing with opentelemetry

### Fixed

- Rethink how it gets the context
- Rename start span to noun

## [28.12.0] - 2025-07-02

### Added

- Add config base
- Add missed default

### Changed

- Yaml based settings foundation
- Yaml-based settings extended with old settings
- Use new settings
- Option for missing section
- Merge conflict
- Rename FrameworkSettings to Settings

### Removed

- Remove magic strings

## [28.11.0] - 2025-07-01

### Changed

- Set index._space_schemas
- Simplify IN creation

### Fixed

- Proper weighing of cfns
- List to Sequence in index

### Removed

- Remove space from GroupKey
- Remove unreachable code

## [28.10.0] - 2025-06-27

### Changed

- Create an initialization method for metrics

### Fixed

- Dependency issues
- Changing dict type to allow any

## [28.9.0] - 2025-06-23

### Fixed

- Merge issues resolved

## [28.8.2] - 2025-06-19

### Added

- Add opentelemetry registry
- Add topk vdb connector

### Changed

- Rewriting the metric registry

### Fixed

- Redis version
- Redis ordering issue
- Rewrite topk index creation logic

### Removed

- Remove redis health_check_interval that caused timeout

## [28.8.1] - 2025-06-19

### Removed

- Remove refresh from async redis client

## [28.8.0] - 2025-06-19

### Added

- Support nlq openai custom base_url

## [28.7.0] - 2025-06-18

### Changed

- Update modal version - does not break anything
- Update model dimension cache

## [28.6.0] - 2025-06-18

### Changed

- Pin aiohttp version

## [28.5.1] - 2025-06-17

### Added

- Added missing async for read_node_result, more resilient async handling, redis improvements

## [28.5.0] - 2025-06-17

### Changed

- Improve modal with oom safety

## [28.4.1] - 2025-06-16

### Fixed

- Fix RuntimeError: cannot reuse already awaited coroutine

## [28.4.0] - 2025-06-16

### Changed

- Introduce redis connection pool

## [28.2.0] - 2025-06-12

### Added

- Add ModelEngineConfig to init

### Changed

- Better config for modal

## [28.1.5] - 2025-06-11

### Changed

- Make search index creation sync

### Fixed

- Mitigate model download issue

## [28.1.4] - 2025-06-11

### Fixed

- Fix model partial download issue in batch workers

## [28.1.3] - 2025-06-10

### Changed

- Make query evaluation (redis, nlq) async
- Introduce async_lazy_property
- Make search index creation sync
- Rephrase error msg

### Fixed

- Use constant for hf_hub_prefix

### Removed

- Remove model name prefix

## [28.1.2] - 2025-06-10

### Fixed

- Embedding engine manager to be actual singleton

## [28.1.0] - 2025-06-08

### Added

- Add configurable search settings for Redis

## [28.0.0] - 2025-06-05

### Changed

- Redis add type to query
- Use singleton embeddingengine manager

### Fixed

- Handle texts in openclip in fp16 + change default to fp16 when gpu is available

### Removed

- Remove not needed register_engine and add model_dimension_cache

## [27.6.1] - 2025-06-04

### Changed

- Rename EngineManager -> EmbeddingEngineManager
- Introduce EmbeddingEngineManagerFactory
- Batch alignment related changes
- Improve caching performance
- Improve norm and concat performance

### Fixed

- Version passing to server's update

### Removed

- Remove SUPERLINKED_MODEL_CACHE_SIZE env var

## [27.6.0] - 2025-06-03

### Added

- Added boolean type to hard filter nb
- Added boolean_field.not_in_()

### Fixed

- Multiple syntax

## [27.5.0] - 2025-06-02

### Changed

- Introduce boolean.field.is_ and boolean.field.is_not_

## [27.4.0] - 2025-06-02

### Changed

- Update toml

### Removed

- Remove infinity to enable running the notebooks on colab

## [27.3.0] - 2025-06-02

### Changed

- Deploy notebooks

### Fixed

- Fix notebooks not being compatible with colab

## [27.2.2] - 2025-06-02

### Changed

- Update redisvl version

## [27.2.1] - 2025-05-30

### Fixed

- Update python.yml

## [27.2.0] - 2025-05-30

### Added

- Add sensible defaults for performant hybrid search in redis

### Changed

- Merge main
- Revert change for concurrent effect evaluation

## [27.1.0] - 2025-05-29

### Changed

- Dependency update trigger for superlinked-server

## [27.0.0] - 2025-05-26

### Changed

- Replace Text with Tag field in redis
- Change back tagtext to text

## [26.0.0] - 2025-05-26

### Changed

- Improve redis latency during load with metadata tag fields
- Better comment
- Tag metadata index pr as breaking

## [25.0.0] - 2025-05-23

### Added

- Add support for python 3.12.4
- Added support 3.12.10

### Changed

- Faster redis queries - tag and unf
- Introduce boolean field
- Full text to schema id rename
- Merge leftover

## [24.0.0] - 2025-05-21

### Added

- Add dag displayer
- Add legends to dag displayer

### Changed

- Concurrent effect evaluation
- Bump matplotlib
- Merge main
- Clean up comments
- Build config params dict properly

### Fixed

- Embedding node id
- Schema field node id
- Image space equality
- Set proper visibility in dag displayer

### Removed

- Remove comments
- Remove linefeed

## [23.9.0] - 2025-05-20

### Added

- Add search_algorithm arg to QdrantVectorDatabase

### Changed

- Introduce EngineManager
- Revert cpu_count change
- Revert modal renaming

### Fixed

- Model_downloader concurrency issue

## [23.8.0] - 2025-05-20

### Added

- Added partial scores to help explanation. Also to query_result as a general piece

### Changed

- Extended weight explanations in feature nb

## [23.7.0] - 2025-05-18

### Changed

- Improve modal image embedding performance

## [23.6.1] - 2025-05-17

### Fixed

- Rename args

## [23.6.0] - 2025-05-17

### Changed

- Vector aggregation combine negative filters

### Fixed

- Negative_filter_indices in vector operations

### Removed

- Remove unnecessary arg

## [23.5.0] - 2025-05-15

### Added

- Add grpc configurability for qdrant

## [23.4.0] - 2025-05-13

### Changed

- Retry logic for OEAN metadata write

## [23.3.0] - 2025-05-13

### Changed

- Modal setting for minimum latency

## [23.2.1] - 2025-05-12

### Removed

- Removed old code

## [23.2.0] - 2025-05-08

### Changed

- Improved modal performance and added Settings.SUPERLINKED_RESIZE_IMAGES

## [23.1.0] - 2025-05-06

### Changed

- Rename persist_evaluation_result to persist_node_result
- Rename persist_parent_evaluation_result to persist_parent_node_result

## [23.0.0] - 2025-04-29

### Added

- Added SearchAlgorithm to sl.init
- Add concurrent executor to events and change default env vars

### Changed

- Ability to change search algorithm for redis

### Fixed

- Fix json parser parsing None schema references as string and concurrency problem

## [22.17.1] - 2025-04-29

### Fixed

- Catch HfHubHTTPError

## [22.17.0] - 2025-04-28

### Changed

- Improve logging - remove long logger name, some renaming of vars

## [22.16.1] - 2025-04-24

### Fixed

- Fixed modal docs
- Fixed number with_vector weight bug

## [22.16.0] - 2025-04-24

### Added

- Add modal handler
- Added modal dependency

### Changed

- Improve infinity manager
- Infinity remove log

### Removed

- Remove blob_handler cache

## [22.15.2] - 2025-04-24

### Fixed

- Not all effects were evaluated

## [22.15.1] - 2025-04-22

### Fixed

- Proper projection to dag effect in an
- Proper traverse of dag for dag effect

## [22.15.0] - 2025-04-16

### Changed

- Implement image embedding support for infinity

## [22.14.1] - 2025-04-15

### Added

- Add text model handler to exports

### Changed

- Publish DescribedBlob in sl

### Fixed

- Dataframe parser with nullable fields and columns
- Not reusing variables

## [22.13.1] - 2025-04-14

### Fixed

- Reduce number of load_stored_results calls

## [22.13.0] - 2025-04-10

### Changed

- Vector multiplication without affecting the negative filters

### Fixed

- Missing type

## [22.12.0] - 2025-04-10

### Changed

- Make value immutable

## [22.11.0] - 2025-04-10

### Changed

- Only embed unique values
- Performance improvements

## [22.10.0] - 2025-04-09

### Changed

- Do not evaluate non-unique affecting
- Group load_stored_results reads
- Revert oean change

## [22.8.0] - 2025-04-08

### Changed

- Batched event evaluation
- Rename datas to data_items
- Eliminate indentation
- Improve readability

## [22.7.0] - 2025-04-07

### Added

- Add infinity api for text embedding
- Add missing asserts

### Changed

- Update sentence transformer

### Fixed

- There are two inputs

## [22.6.4] - 2025-04-03

### Fixed

- Introduce redis timeout 10s

## [22.6.2] - 2025-03-31

### Fixed

- Better nlq error handling

## [22.6.1] - 2025-03-31

### Fixed

- Reduce serialization overhead of vectors

## [22.6.0] - 2025-03-26

### Added

- Add timeout argument to qdrant

## [22.5.0] - 2025-03-25

### Fixed

- Revert metadata key to node_id

## [22.4.0] - 2025-03-25

### Changed

- Argument matchers for mock call assertions
- Sanitize qdrant field names
- Disable in toml instead at every import

### Fixed

- Fix docstring

## [22.3.1] - 2025-03-24

### Changed

- Update pip

### Fixed

- Only decode existing vectors/fields

### Removed

- Remove as it is unnecessary

## [22.3.0] - 2025-03-20

### Changed

- Store vectors as fp16 by default

## [22.2.0] - 2025-03-20

### Changed

- Ignore futurewarning

## [22.1.2] - 2025-03-20

### Added

- Support hard filters for optional fields

### Changed

- Save

## [22.1.1] - 2025-03-20

### Fixed

- Better exceptions for blobhandler

## [22.1.0] - 2025-03-19

### Changed

- Vector part accessing feature notebook

### Fixed

- Image search notebook outputs

## [22.0.1] - 2025-03-19

### Fixed

- Improve logging performance

## [22.0.0] - 2025-03-19

### Changed

- Node-id changed!  - support hugging face api embedding

## [21.3.1] - 2025-03-18

### Fixed

- DataFrame parser + collection util
- String is iterable

### Removed

- Removed commit

## [21.3.0] - 2025-03-18

### Changed

- Concurrent blob loading

## [21.1.0] - 2025-03-17

### Changed

- Implement SUPERLINKED_MODEL_CACHE_SIZE

## [21.0.0] - 2025-03-17

### Added

- Add should_return_index_vector
- Add schema field selector

### Changed

- Use should_return_index_vector
- Return vector parts

### Fixed

- Rename ambiguous method
- Adjust notebooks to changed select syntax

### Removed

- Remove CHANGELOG.md

## [20.5.0] - 2025-03-14

### Removed

- Remove graphviz from extras

## [20.4.0] - 2025-03-14

### Added

- Add exception visualization

### Changed

- Implement dag visualizer for online and query dag
- Update deps

## [20.3.2] - 2025-03-14

### Changed

- Per-space with_vector weights feature nb

### Removed

- Removed double preprocess for images, and refactor

## [20.3.1] - 2025-03-14

### Changed

- Return instantly

### Fixed

- Categorical similarity inverse embed
- Other_category_name

## [20.2.0] - 2025-03-13

### Added

- Add todos
- Add _validate_get_vector_parts_inputs

### Changed

- Set proper query node method visibilities
- Introduce get_vector_parts
- Update astroid dep and restrict dep bot

## [20.1.1] - 2025-03-12

### Added

- Add proper comment on type ignore
- Add incorrectly removed backtick

### Changed

- Double-check visibilities
- Revert run on save changes
- Merge main
- Schemafield.as_type

### Fixed

- Use if none fail
- Separate ParamInputType and None
- Mostly naming changes
- Rename clause.get_defautls
- Error message adjustment
- Dataframe parser for arrays

### Removed

- Remove unnecesarry setUp

## [20.1.0] - 2025-03-10

### Changed

- Merge main into ras-421
- Move explanations to markdown cells
- Enhance categorical_embedding notebook structure and content
- Clean run
- Rename sources
- Dummy commit to trigger release pipeline
- Update notebook introduction

### Fixed

- Fix

## [20.0.0] - 2025-03-10

### Changed

- Do not include not needed fields in node id

### Fixed

- Node_id creation to be deterministic

### Removed

- Remove unwanted dag_effects from ean as it is present in cfn (parent of ean)

## [19.22.0] - 2025-03-10

### Changed

- Allow lazy init of gcs client

## [19.21.2] - 2025-03-10

### Fixed

- Handle empty redis string list

## [19.21.1] - 2025-03-07

### Added

- Add missing _set_param_name_if_unset

### Changed

- Nlq annotation
- Query param model validator refactor
- Introduce SpaceWeightParamInfo
- Refactor get_param_value_for_unset_space_weights
- Set param defaults on clause
- Split query clauses
- Move validation to clauses
- Check QueryClause attribute visibility
- Introduce base looks like filter clause
- Nlq compatible clause handler
- SingleValueParamQueryClause
- Introduce WeightBySpaceClause
- Introduce SpaceWeightMap
- Negative_filter_indices property

### Fixed

- Init clauses only with from param
- Move set default for nlq
- Fix-python
- Weight by space clause get weight value
- Number embedding default vector negative_filter

### Removed

- Remove clause.evaluate
- Remove QueryClause generics
- Remove space weight clause
- Remove HasAnnotation

## [19.21.0] - 2025-03-06

### Changed

- Resolve merge conflict

## [19.19.1] - 2025-03-05

### Changed

- Initial commit with updated notebook
- Notebook unintended change

### Fixed

- Categorical space similar input pattern insensitivity
- Categorical embedding normalization+
- Collection util

## [19.18.0] - 2025-03-05

### Added

- Add redis client refreshing logic

### Changed

- Better docstring for idfield

## [19.17.1] - 2025-03-05

### Added

- Support non-default schema id and created_at access

## [19.16.0] - 2025-03-04

### Changed

- Mac/gnu shed is different
- Faster storage.Client init
- Use dataclass to store params
- Move inner class outside
- Mark deprecated functions
- Ability to evaluate dag concurrently

### Fixed

- Apply Teddys fix

## [19.15.1] - 2025-03-03

### Added

- Add readtimeout error retrial for model download

## [19.15.0] - 2025-02-27

### Changed

- Moved IdField into separate class
- IdField filtering works with inmemory
- IdField filtering works with redis and qdrant
- IdField filtering works with mongo
- Batched write_node_result instead of single calls
- Rename write_node_result to write_node_results

## [19.14.2] - 2025-02-26

### Added

- Add QueryNodeInputValue
- Add get_generic_types_of_class to generic class util
- Add title to rounds

### Changed

- Udpate deps
- Declare default dict generic type
- Refactor param modification of clauses
- Introduce TypedParam
- Use TypedParam vol 1
- Convert int to float
- Query clause unification part 1
- Composit TypedParam
- Clause as source of truth
- Adjust with_vector docstring
- Introduce QueryClause.get_value_by_param_name
- Order _to_typed_param args
- Data stream observer
- Storage usage evaluator
- Vdb watcher
- Introduce storage usage report
- StorageUsageReport.to_csv

### Fixed

- Adjust exception handling in stm to poetry update
- Hard filter integration
- Base prompt syntax
- Params with option error msg check
- With_vector_weights_integration
- Instructor prompt integration
- Move longest input len calc
- Any with set
- Nlq prompt if simplification
- Invert if in set_defaults_for_nlq
- Looks like clause __get_weight reorder ifs
- Assert result in select clause integration
- Calc weight param related changes separately
- Rename data size in report
- Handle none snapshot
- Handle created_at with dataframes correctly
- Allow int inputs for float schemafield params

### Removed

- Remove _transform_param_value
- Remove query predicate module
- Remove original options
- Remove magic string from query clause
- Delete qdrant snapshot

## [19.14.1] - 2025-02-26

### Changed

- Cast sequence to list when accessing as a list
- Make points_by_entity_id more readable

### Fixed

- Introduce default_factory=dict for QueueConfig dataclass

## [19.14.0] - 2025-02-25

### Fixed

- Feature notebook

### Removed

- Removed weighting from vector_sampler

## [19.13.0] - 2025-02-24

### Changed

- Introduce SUPERLINKED_EXECUTION_TIMER_INTERVAL_MS

## [19.12.0] - 2025-02-21

### Added

- Add timer calls
- Added new timers
- Added timer decorator
- Added ENABLE_PROFILING env var

### Changed

- Implement ExecutionTimer
- Improve execution_timer
- Timer for gcs blob

## [19.11.0] - 2025-02-18

### Changed

- Introduce index.schemas to allow access in batch

## [19.10.0] - 2025-02-17

### Added

- Add validation for hard filter for non-schema field

## [19.9.0] - 2025-02-14

### Changed

- Allow select clauses with id field
- Filter out id field in a better way

## [19.8.0] - 2025-02-13

### Changed

- Validation for supported comparison operation types

## [19.7.3] - 2025-02-12

### Fixed

- Handle hf timeout error

## [19.7.2] - 2025-02-11

### Fixed

- Rework qdrant hard filter handling - handle or, float, stringlist, contains, in

### Removed

- Remove numberutil

## [19.7.1] - 2025-02-10

### Fixed

- Default space weight param did not take affect

## [19.7.0] - 2025-02-10

### Added

- Add model cache to text embedding config
- Add model cache to image embedding config

### Removed

- Remove FAI-1909
- Remove FAI-2843
- Remove FAI-2085
- Remove FAI-1931
- Remove FAI-2391

## [19.5.0] - 2025-02-05

### Added

- Add correct device handling for image embeddings

## [19.4.1] - 2025-02-04

### Changed

- Rename var

### Fixed

- With_vector flag on qdrant querying

## [19.4.0] - 2025-02-04

### Added

- Add optional index vector to SearchResultItem
- Add partial scores to results

### Changed

- Return index vector if metadata was requested
- Resolve merge conflict

## [19.3.0] - 2025-02-04

### Added

- Add include_metadata arg to query
- Add partial scores to query results

### Changed

- CategoricalNorm
- CategoricalNormalization strategy
- CategoricalNorm in CategoricalSpace

### Fixed

- Magic constants in embedding

### Removed

- Removed leftover code

## [19.2.2] - 2025-01-30

### Fixed

- Trigger build

## [19.2.1] - 2025-01-30

### Fixed

- Trigger build

## [19.2.0] - 2025-01-30

### Added

- Added signed sum common util
- Added ListUtil and made VectorUtil use it

### Changed

- VectorAveraging aggregation strategy
- Adjust query vector step (fix with_vector bug)
- CategSimilaritySpace revamp
- Adjusted feature notebook to new working
- Update poetry
- Gpu util
- Bump upload artifact version
- _calculate_partial_scores

### Fixed

- Vector.aggregate negative_filter bug
- Fix astroid version
- Move astroid dependency to dev group
- Only add if available
- Gpu tensor
- Fix merge

### Removed

- Remove print

## [19.1.0] - 2025-01-30

### Removed

- Remove the object json persisting functionality

## [19.0.0] - 2025-01-28

### Changed

- Query result feature notebook extended

### Fixed

- Adapt a new notebook to the new query result schema

## [18.9.0] - 2025-01-24

### Changed

- Optional schema field feature nb

## [18.8.0] - 2025-01-22

### Changed

- Enable online schema field node to return none
- Moer readable SpaceFieldT

### Fixed

- Space input validation
- Var name

## [18.7.1] - 2025-01-22

### Added

- Add next iter

### Fixed

- Modify error message of validate parents

## [18.7.0] - 2025-01-21

### Added

- Add query result converter for rest app
- Add default query result converter
- Add Node._non_nullable_parents
- Add batch read node result to storage manager

### Changed

- Restructuring the query result object
- Pandas converter introduction and result migration to pydantic
- Adapt the new result schema in the notebooks
- Set non_nullable_parents
- Evaluate parents, validate parent results
- Optional online node result
- Load stored results in batch

### Fixed

- Select clause should contain reference
- Wrong reference in notebooks
- Removing a todo
- Too long line
- Simplify validate parents result

### Removed

- Remove unnecessary comment

## [18.6.0] - 2025-01-17

### Changed

- Blob_loader config as argument

## [18.5.0] - 2025-01-17

### Changed

- Missing override, unnecessary instance var
- Schema attribute annotation info
- Check optional attributes in event schemas
- Extend schema field with is_optional
- Rename is_optional to nullable

### Fixed

- Adjust error message

### Removed

- Remove leftover

## [18.4.0] - 2025-01-13

### Changed

- Use entire group of large runners

## [18.3.0] - 2025-01-10

### Fixed

- Decrease complexity of init image embedding node

## [18.2.0] - 2025-01-09

### Added

- Added query result select clause feature notebook
- Added str and repr to ParsedSchemaField

### Changed

- Move calls after init in spaces wherever could
- Smart if
- Extended feature nb and clarified it

### Fixed

- Unpack clause eval result
- Separate image field validation from split

### Removed

- Remove schema field from similar query clause
- Remove leftover

## [18.1.1] - 2025-01-09

### Fixed

- Removing the to snake call from query names

## [18.1.0] - 2025-01-09

### Added

- Add main protection section to CONTRIBUTING.md
- Add APP_ID settings

## [18.0.1] - 2025-01-08

### Fixed

- Raise error if mismatching input and vector in embedding cache

## [18.0.0] - 2025-01-07

### Changed

- Sentence transformer to automatically fill prompt_name kwarg

## [17.9.2] - 2025-01-06

### Fixed

- Make model loading more resilient

## [17.9.1] - 2025-01-06

### Fixed

- In_ filters were not grouped for redis

## [17.9.0] - 2025-01-06

### Added

- Added comment regarding FieldCondition casting

### Changed

- Rename returned_fields to fields_to_return
- Move schema fields initialization to init
- Changed __handle_select_param error msg
- Moved the underscore to the end of the default param names
- Changed FieldCondition casting to list

## [17.8.3] - 2025-01-03

### Changed

- Do not allow similar clause for recency and number min max
- Change exception message

### Fixed

- Fix nlq number space annotation and better exception name for similar not allowed
- Fix allow_similar_clause return type

## [17.8.2] - 2025-01-02

### Added

- Add validation for categories in categorical space

## [17.8.1] - 2025-01-02

### Added

- Add validation for categories type in categorical space

### Fixed

- Handle Vector type in query number input processing

## [17.8.0] - 2024-12-19

### Changed

- Move nlq_clause_collector
- Improve prompts

### Fixed

- Fix prompt problem

## [17.7.0] - 2024-12-12

### Added

- Add image util
- Add open local image file

## [17.6.0] - 2024-12-12

### Changed

- Make the ingestion more performant
- Rethink input parameters of storage manager

## [17.5.0] - 2024-12-11

### Changed

- Default returned fields to all schema fields
- Move None interpretation to knn_search method

### Fixed

- Naming

## [17.4.0] - 2024-12-10

### Changed

- Enable bulk read for mongodb

## [17.3.0] - 2024-12-10

### Changed

- Rethink the structure how the storage manager returns the items
- Properly handle the ids in case of chunking

## [17.2.2] - 2024-12-06

### Changed

- Handle tensor size mismatch in encoding

### Fixed

- Allow query with result.knn_params

## [17.2.1] - 2024-12-06

### Added

- Add create_search_indices param

## [17.2.0] - 2024-12-05

### Added

- Add ignore list parameter to class helper

## [17.1.0] - 2024-12-03

### Added

- Add schema to embedding node inits

## [17.0.1] - 2024-12-02

### Changed

- Rename _node_by_schema
- Rename get_all_leaf_nodes

### Fixed

- Typing in schema fields

## [17.0.0] - 2024-12-02

### Changed

- Input type annotations to use Sequence

## [16.3.0] - 2024-12-01

### Changed

- Event effect feature nb up-to-date

## [16.2.0] - 2024-11-29

### Added

- Add a new check for base64 encoded bytes if it's not allowed

## [16.1.8] - 2024-11-29

### Fixed

- Adjusted event effect notebook to event_influence change

## [16.1.6] - 2024-11-27

### Fixed

- RecencyEmbedding.__get_expiry_date

## [16.1.5] - 2024-11-27

### Changed

- Update poetry
- Increase perf treshold
- Naming

### Fixed

- Z value condition
- Period time ref
- Security vulnerability in aiohttp

## [16.1.4] - 2024-11-26

### Fixed

- Fix embedding attribute error

## [16.1.2] - 2024-11-26

### Changed

- Update embedding length calculation and error handling

### Fixed

- Recency embedding

## [16.1.1] - 2024-11-25

### Changed

- Update hash method in EmbeddingNode

## [16.1.0] - 2024-11-25

### Changed

- Trigger update in server and batch

## [16.0.0] - 2024-11-25

### Added

- Adds node ID suffix generation for embedding configs

### Changed

- Trigger update in server and batch

## [15.2.0] - 2024-11-21

### Changed

- L1 weights normalization for events

### Removed

- Remove warp value constraint and optimize single item aggregation

## [15.1.1] - 2024-11-21

### Removed

- Remove stop words from redis index definition

## [15.0.0] - 2024-11-20

### Changed

- SentenceTransformerCache to SentenceTransformerModelCache

## [14.7.1] - 2024-11-20

### Added

- Add init search indices flag to apps
- Add init search inidices flag to rest app

### Changed

- Make search index creation configurable in interactive app
- Rewrite set operation

### Fixed

- Validate list as Param.options

## [14.7.0] - 2024-11-19

### Changed

- Deterministic hash of of strings
- Introduce app_id as collection name
- Rename mongo to mongo db

### Fixed

- Empty update operations
- Qdrant check and get vectors

## [14.6.1] - 2024-11-19

### Fixed

- Release fixed links

## [14.6.0] - 2024-11-19

### Added

- Added Param options to NLQ feature nb

## [14.5.0] - 2024-11-19

### Added

- Add more detailed error message

### Fixed

- Vdb imports

### Removed

- Remove type ignore

## [14.4.1] - 2024-11-18

### Fixed

- Notebook extra query params removed

## [14.4.0] - 2024-11-18

### Added

- Add QdrantVDBConnector to framework init

### Changed

- Simplify field encoder
- Upsert, update vectors, set payload + batch
- Allow extra params in settings

### Fixed

- Sentence transformer initialization bug
- Pydantic internal change
- Pydantic issue
- Changing to extra in settings to ignore

## [14.3.0] - 2024-11-13

### Added

- Add QdrantVectorDatabase

### Changed

- Qdrant field encoder
- Qdrant search index manager
- Qdrant search
- Qdrant filters
- Qdrant filters reshaping - WIP
- Write entities
- Read entities
- Integrate qdrant search

## [14.1.1] - 2024-11-13

### Fixed

- Pr

## [14.1.0] - 2024-11-12

### Changed

- Image search nb text fix
- Allow single inputs in dsl

## [13.1.3] - 2024-11-08

### Fixed

- Restore old model cache path

## [13.1.2] - 2024-11-08

### Added

- Add imports

## [13.1.1] - 2024-11-08

### Fixed

- Query compensation factor
- Query concatenation node's normalization

## [12.28.1] - 2024-11-07

### Changed

- Move entity to its own package
- Move field to its own package
- In memory vdb with dynamic sim
- Redis sim
- Mongo sim
- Do not do deprecation warning

### Fixed

- Simplify empty vector implementation

## [12.28.0] - 2024-11-07

### Added

- Add contains_all filter support for vdbs

### Fixed

- Adjust containment check for None handling

## [12.27.0] - 2024-11-06

### Added

- Added missing new line to nlq prompt

## [12.25.0] - 2024-11-06

### Changed

- Return model dimension without model initialization
- Do not download config files only
- Changes in model manager and sentence transformer

### Fixed

- Handle model loading errors with fallback

## [12.24.2] - 2024-11-06

### Fixed

- Default node handling for text, category and custom spacers

## [12.24.1] - 2024-11-06

### Changed

- Stop storing event schema objects in vdb

## [12.23.0] - 2024-11-05

### Removed

- Remove combine_values
- Remove should_load_default_node_input
- Delete query filters
- Remove only-one-similar-per-space restriction
- Remove query related parts of online dag

## [12.22.0] - 2024-11-04

### Changed

- Ported image search use-case nb to ImageSpace

## [12.21.0] - 2024-11-04

### Fixed

- Image embedding similarities

## [12.20.1] - 2024-11-04

### Added

- Added image embedding feature notebook

### Fixed

- Unified feature notebooks' singular space reference

## [12.20.0] - 2024-10-31

### Removed

- Removed semantic search nb extra comment

## [12.19.0] - 2024-10-31

### Added

- Add proper normalization to concatenation nodes

### Fixed

- Paragraph_concatenation_integration

### Removed

- Remove comments

## [12.18.3] - 2024-10-31

### Fixed

- Do not send warning message if gcp services not configured

## [12.18.1] - 2024-10-30

### Changed

- Move merge inputs to ancestor
- Adjust with vector weights integration

### Fixed

- Merge conflicts
- Query number embedding node
- Query recency node input
- Loosen image input validation
- Custom space integration
- Optional param integration
- Adjust categorical similarity space integration
- Resolve embedding dim fallback issue in manager

## [12.18.0] - 2024-10-30

### Added

- Add full path support

### Changed

- Download from authenticated sources
- Eliminate magic string

## [12.17.0] - 2024-10-30

### Changed

- Simplify imports using alias

### Removed

- Removed root init py file, moved root imports one level deeper

## [12.16.0] - 2024-10-30

### Added

- Addressed invertible embedding node

### Changed

- Use new query dag evaluator - WIP
- Multiple parents on embedding node
- Rename _get_node to _get_embeddding_node
- Image space field set
- Adjust query image embedding node to new addressing
- Adjust query vector factory initialization
- Load looks like vector by id
- Rename variable
- Improve error message

### Fixed

- Make online embedding node simple online node

## [12.14.0] - 2024-10-29

### Added

- Add callback to publish feature
- Add the message and type of the exception to the log

## [12.13.1] - 2024-10-29

### Fixed

- Customize model dir for transformers

## [12.13.0] - 2024-10-29

### Changed

- Nb

## [12.10.0] - 2024-10-28

### Changed

- Query image nodes - WIP
- Introduce query evaluation result

### Removed

- Remove comments

## [12.9.0] - 2024-10-28

### Added

- Add unquote to URLs

## [12.8.0] - 2024-10-28

### Changed

- Handle query params in file name discovery

## [12.7.3] - 2024-10-28

### Changed

- Update typing imports in query_clause

## [12.7.2] - 2024-10-28

### Added

- Added NLQ notebook to checkout to other branch

## [12.7.1] - 2024-10-25

### Changed

- NLQ notebook on more realistic searches
- Refactor query dsl with todo items
- Some more refactor on query dsl with todo items
- Introduce mandatory clauses
- Handle space weight missing values in query
- Introduce QueryClause.evaluate
- Re-introduce knn_params
- Allow params with the same name

### Fixed

- Applied with_vector fix
- Fix serialization issue with blob info
- Use meaningful names as variables
- Blob handling issues with base64 encoding

### Removed

- Removed data wrangling from notebook

## [12.6.0] - 2024-10-25

### Changed

- Enforce strings in dataframe parser
- Introduce query dag
- Compiled node registry
- Query dag compiler
- Query dag evaluator
- Rename vars

### Fixed

- Move online dag evaluator to online dictionary
- Pr items
- NODES_TO_EXCLUDE

### Removed

- Remove unnecessary methods

## [12.4.0] - 2024-10-24

### Changed

- Introduce json field data type

### Fixed

- Rename object_blob to object_json
- Blob infromation readability

## [12.3.0] - 2024-10-24

### Changed

- Query node base
- Use mapping instead of dict
- Query index node - WIP
- Query index node
- Query concatenation node
- Query aggregation node
- Query constant node
- Query named function node
- Query custom vector embedding node
- Query number embedding node
- Query categorical similarity embedding node
- Query recency node
- Query text embedding node
- Poetry update

### Fixed

- Variable name
- Pr items

### Removed

- Remove typing_protocol_intersection

## [12.2.0] - 2024-10-22

### Removed

- Remove aggregation type
- Remove embedding type
- Remove normalization config

## [12.1.0] - 2024-10-22

### Added

- Add the skeleton for blob upload

### Fixed

- Resolve comments

## [11.1.0] - 2024-10-21

### Added

- Added NLQ to RAG notebook + used env variable for API key

### Fixed

- Transfomers warning

## [11.0.0] - 2024-10-21

### Added

- Add input type to embedding config
- Add to_dict to configs
- Add skip weighing wrapper

### Changed

- Update notebooks
- Clean up

### Fixed

- 0 vector when no event
- Bulk st embedding
- Recency plotter
- Gen instead of list

## [10.2.2] - 2024-10-14

### Fixed

- All spaces to have default node, and OnlineConcatenationNode refactor

## [10.2.0] - 2024-10-14

### Changed

- Experimenting
- Revert not needed files

### Fixed

- Prevent mismatched schemas in index creation

## [10.1.1] - 2024-10-11

### Added

- Add factories
- Add generics to AN and EAN

### Changed

- Introduce step and transformer
- Normalization step
- Aggregation step
- Embedding step
- Rename folder
- Configs
- Port old embeddings
- Pass generics to embedding node
- OCSN
- OCustomN
- ONEN
- ORN
- Move effect modifier

### Fixed

- Correct import

### Removed

- Remove has embedding
- Remove embeddings
- Remove legacy
- Remove unsused args of EN

## [10.1.0] - 2024-10-09

### Changed

- Use structured dict for stacktraces

## [10.0.0] - 2024-10-08

### Changed

- Unify embedding logic under EmbeddingNode
- Unify params to config in categorical components

### Removed

- Remove redundant interfaces from embeddings
- Remove casting

## [9.48.6] - 2024-10-07

### Fixed

- Rename vector alias and change sorting logic

## [9.48.4] - 2024-10-04

### Fixed

- Notebook table counts

## [9.48.2] - 2024-10-04

### Fixed

- Repomerge should now copy docs to the correct directory

## [9.48.1] - 2024-10-03

### Changed

- Improve performance

### Fixed

- Restrict the data type to only send dict messages

## [9.48.0] - 2024-10-02

### Added

- Add schema_id to published messages

### Changed

- Introduce MessageT

## [9.47.1] - 2024-10-02

### Fixed

- Activity distribution text in user acquisition nb

## [9.47.0] - 2024-09-30

### Added

- Support TypeVar in type validation

### Changed

- Update logging string in interactive_executor.py

### Fixed

- Restore None as an option for vector_database in InMemoryApp

## [9.46.3] - 2024-09-27

### Fixed

- Last touches

## [9.46.1] - 2024-09-27

### Fixed

- Image search notebook text issue

## [9.46.0] - 2024-09-26

### Added

- Add interactive source
- Add InteractiveApp

### Changed

- Interactive executor
- Update docstrings for interactive and inmemory executors
- Update docstrings
- InMemoryExecutor is a child of InteractiveExecutor
- InMemorySource is a child of InteractiveSource
- Made renderer environment aware

## [9.45.0] - 2024-09-26

### Changed

- Default param to NLQ feature nb

## [9.44.0] - 2024-09-26

### Added

- Added default info on params to corresponding feature nb

## [9.43.1] - 2024-09-26

### Removed

- Removed note about colab compatibility

## [9.43.0] - 2024-09-25

### Changed

- Catching any caching issues

## [9.42.1] - 2024-09-25

### Fixed

- Disable warning messages only show them if the queue is not correctly configured

## [9.42.0] - 2024-09-24

### Changed

- Warn if queue params are none

## [9.41.1] - 2024-09-24

### Fixed

- Cluster label mixup
- User acq nb summary table

## [9.40.0] - 2024-09-24

### Added

- Add super calls and fix list comprehension

## [9.38.1] - 2024-09-23

### Added

- Add super calls and fix list comprehension

### Fixed

- Fix type issue

## [9.38.0] - 2024-09-23

### Changed

- Changed embedding model to a more general vision transformer
- Restrict dependabot for only patch and minor versions
- Restrict only patch and minor

## [9.37.0] - 2024-09-18

### Changed

- Modify default cache size

## [9.36.0] - 2024-09-17

### Changed

- Update contributing.md, remove comments

### Fixed

- Improve readability
- Load queue args with json loads

## [9.35.1] - 2024-09-17

### Removed

- Remove source queue mapping, use simply 1 queue

## [9.34.0] - 2024-09-12

### Added

- Add on error logging to pub sub
- Add logging info to README

### Changed

- Improve readability
- Decouple queue and online source
- Queue factory
- Image search usecase notebook
- Updated usecase to better showcase power
- Refactor logging so deployment can easily adapt
- Separate node log arguments to id and type
- Reintroduce log_as_json

### Fixed

- Missing negation
- Fix performance issue

## [9.33.0] - 2024-09-10

### Changed

- Attempt to fix versioning
- Revert version_variables
- Avoid name clashing in result, and added rank

### Fixed

- Incorrect variable name

## [9.32.1] - 2024-09-09

### Changed

- Capture remove

### Fixed

- Plot legend color

## [9.32.0] - 2024-09-09

### Changed

- Refactor logging so deployment can easily adapt

### Fixed

- Missing negation

## [9.31.0] - 2024-09-09

### Added

- Add logging info to README

## [9.30.0] - 2024-09-09

### Added

- Add version variable for semantic-release
- Add logging guidelines

### Changed

- Image search usecase notebook
- Updated usecase to better showcase power

## [9.29.0] - 2024-09-05

### Changed

- Temperature now constant
- Structlog to handle stdlib logs
- Moved package log level setting

## [9.27.2] - 2024-09-04

### Changed

- Handle NoneType in comparison operations

## [9.27.1] - 2024-09-04

### Added

- Support in and contains operation with nlq

## [9.27.0] - 2024-09-03

### Added

- Add queue as args to app

### Changed

- Introduce message converter
- Move validatation to converter
- Initialize queues

### Fixed

- Make queue payload mandatory
- Gcp pub sub as extra
- Replace magic number with named default
- Move default parser to dsl classes
- Separate gcp-related settings from the general ones
- Poetry installation method in contributing

### Removed

- Remove unnecessary 2nd generic of common source
- Remove dsl source
- Remove hardcoded queue message version

## [9.26.0] - 2024-09-02

### Added

- Add "scope" to logs

### Changed

- Implement queues
- Integrate structlog for better logging
- Logger should not override existing process_id

## [9.25.1] - 2024-08-30

### Fixed

- Recency inverse embed multi period time bug

## [9.24.0] - 2024-08-29

### Changed

- Suppress transformers futurewarning

## [9.23.2] - 2024-08-29

### Changed

- Extended hard filter notebook
- Feature nb updates
- Nb merge fix
- Summary structure
- Image embed

### Fixed

- Image url

### Removed

- Removed image

## [9.23.1] - 2024-08-29

### Fixed

- Image asset and removed misleading folder

## [9.23.0] - 2024-08-29

### Added

- Added RAG diagram to RAG notebook

### Fixed

- Image text

## [9.22.0] - 2024-08-28

### Changed

- Feature nb update contains and or

## [9.21.1] - 2024-08-26

### Fixed

- Dataframeparser to accept empty list value

## [9.19.1] - 2024-08-26

### Fixed

- Security vulnerabilities updated

## [9.19.0] - 2024-08-26

### Changed

- Extended hard filter notebook
- 0 temperature and feature nb update accordingly

## [9.18.0] - 2024-08-22

### Changed

- Time related weight clarification

### Fixed

- Unintended notebook commit
- Max_age docstring + feature notebook adjustments

## [9.17.0] - 2024-08-22

### Changed

- Improve embedding model check logic
- Feature notebook adjustment for better filtering

### Fixed

- Fix normalization
- Categorical similarity normalisation

## [9.16.3] - 2024-08-21

### Added

- Add 'Or' class for grouped query filters

### Changed

- Simplify Or clause handling in filtering logic
- Or query
- Or query to hard filter feature nb

### Fixed

- Fix event time modifier
- Sort by VECTOR_SCORE_ALIAS in descending order

## [9.16.2] - 2024-08-15

### Changed

- Undo lazy property

### Fixed

- Build

## [9.15.0] - 2024-08-14

### Added

- Support inmemory and redis LT, LTE, GT, GTE operators for filter
- Support mongodb LT, LTE, GT, GTE operators for filter

### Changed

- Improve performance
- Rename in and not in

## [9.13.0] - 2024-08-14

### Changed

- Notebook outputs

## [9.12.1] - 2024-08-14

### Changed

- Lazy init

### Fixed

- Redis init
- Changed how to check cuda usage with profiler
- Fixing bad performance on calculating the calls for device type

## [9.12.0] - 2024-08-14

### Changed

- Index event rel args + feature nb event type weight info

## [9.9.0] - 2024-08-12

### Changed

- Querying notebook extended
- Extended docstring

## [9.8.0] - 2024-08-09

### Changed

- Extended event effect nb

### Fixed

- Fixed comment

### Removed

- Removed unnecessary effect

## [9.7.2] - 2024-08-09

### Changed

- Feat number embedding nb update log

### Fixed

- Total_seconds bug in effect

## [9.7.1] - 2024-08-08

### Added

- Add context time to query context

### Fixed

- Query now bug

## [9.7.0] - 2024-08-07

### Added

- Add gpu util to decouple gpu stuff from sentence transformers class
- Add copyright text
- Add proper settings and small refactor around bulk gpu embedding

### Changed

- Gpu type is configurable and works above a configured count
- Some changes to resolve the comments
- Small improvements to align with the comments
- Gpu type discovery added

## [9.6.0] - 2024-08-06

### Changed

- Improved prompt on examples and using gpt4

## [9.4.0] - 2024-08-05

### Changed

- Natural language querying feature nb

## [9.3.1] - 2024-08-02

### Fixed

- Negative weight not applied on first event

## [9.3.0] - 2024-08-02

### Changed

- Improve nlq instructor prompt

## [9.2.0] - 2024-08-02

### Changed

- Make default query limit configurable from the outside

## [9.1.1] - 2024-08-02

### Added

- Add default search limit per vdb
- Add constant for -1 value in vdb connector

### Changed

- Move constants
- Give context about default search limit numbers in mongo and redis

### Fixed

- Event arithmetics improvements

### Removed

- Remove the option to give any vector database to in memory executor

## [9.1.0] - 2024-08-01

### Changed

- Knn params
- Renaming

## [8.13.0] - 2024-08-01

### Added

- Add persist and restore to vdb base class

## [8.12.1] - 2024-07-31

### Changed

- Favor over prefer

### Fixed

- Allowing any 2.x.y pandas
- Semantic search leftover Param

## [8.12.0] - 2024-07-31

### Changed

- Move id generation logic to vdb connector

### Fixed

- Rest source issue

### Removed

- Remove field identifier from object serializer

## [8.11.0] - 2024-07-30

### Changed

- Space annotation improvements

## [8.10.0] - 2024-07-29

### Changed

- Sentence transformers 3.0 bump
- Update instructor prompt
- Make nlq evaluator more robust
- Looks_like_filter with 0 weight evaluate to None
- Introduce nlqpydanticmodelbuilder

### Fixed

- Fix no empty line after copyright text

## [8.9.0] - 2024-07-25

### Fixed

- Resolve comments

## [8.8.2] - 2024-07-25

### Fixed

- Bump instructor to fix cohere bug

## [8.8.0] - 2024-07-22

### Changed

- Is_weight -> is_unset_weight

## [8.7.4] - 2024-07-22

### Changed

- RAG notebook beautification
- Simplify logic

## [8.7.3] - 2024-07-22

### Fixed

- Rag notebook issues

## [8.7.2] - 2024-07-22

### Fixed

- Concatenation_node to use l2 norm

## [8.7.1] - 2024-07-19

### Fixed

- Broken link in OSS README

## [8.6.8] - 2024-07-18

### Changed

- Poetry update

## [8.6.7] - 2024-07-18

### Fixed

- Bumped repomerge version

## [8.6.5] - 2024-07-18

### Fixed

- Bumped repomerge version
- Bumping repomerge version

## [8.6.4] - 2024-07-18

### Added

- Add clear etas

### Changed

- Pgvector, supabase, neon, elastic search, weaviate - vdb discovery
- Vdb discovery - chroma
- Vdb discovery - milvis, clickhouse, pinecone
- Vdb discovery - astra db
- Vdb discovery - vertex ai
- Poetry update
- Search index creation clarifications
- Clarify pinecone's collection term
- Updated repomerge revision

### Fixed

- Pr
- Miswording

## [8.5.2] - 2024-07-17

### Fixed

- Use self instead of online app

## [8.5.1] - 2024-07-17

### Changed

- Create online app instead of online execution manager
- Introduce EvaluatedParam class
- Introduce EvaluatedQueryParams

### Fixed

- Resolve comments

## [8.5.0] - 2024-07-16

### Added

- Add openai client skeleton

### Changed

- Implement open_ai client

## [8.4.1] - 2024-07-16

### Changed

- Extract online execution and query functions from in memory app

## [8.2.0] - 2024-07-14

### Changed

- Switch to 'Self' from 'typing_extensions'
- Typing -> beartype.typing

## [8.1.0] - 2024-07-14

### Added

- Added usefulness to RAG notebook

### Changed

- Introduce space annotation
- Made space annotation dynamic

## [8.0.0] - 2024-07-11

### Added

- Added overview to Natural Language Interface for Query Implementation

### Changed

- Not allow optional param for similar, and with_vector filter
- Change default limit to 20
- Change default limit to -1
- Natural Language Interface for Query Implementation dd draft

### Fixed

- Make w.a. methods static

## [7.5.0] - 2024-07-10

### Changed

- Make storage manager init as an abstract method

## [7.4.0] - 2024-07-09

### Changed

- Refactor weight arithmetics
- Poetry update
- Rename variable

## [7.3.0] - 2024-07-09

### Changed

- Extracting vector arithmetics

### Removed

- Remove import

## [7.2.0] - 2024-07-04

### Changed

- Refactoring the executor and application
- Small docstring changes

## [7.1.0] - 2024-07-01

### Changed

- Rename mongodb external classes
- Rename mongo to mondo db

## [7.0.6] - 2024-07-01

### Fixed

- Solve the distutil issue

## [7.0.5] - 2024-06-27

### Fixed

- Correct doc references to accommodate the new structure

## [7.0.1] - 2024-06-24

### Fixed

- Triggering a patch release

## [7.0.0] - 2024-06-24

### Changed

- Rename inverse_embed_adjusted to inverse_embed_adjust
- EventAggregator to handle empty vector
- Comment out empty vector weighting
- Update release flag to trigger pdoc tool update

### Fixed

- Fixed header

## [6.10.0] - 2024-06-24

### Fixed

- Recency in the future is mapped to time_period_start
- Notebook results adjusted
- Write entities with empty array of entity_data

## [6.9.0] - 2024-06-23

### Changed

- Adjust README to reflect released server

## [6.8.0] - 2024-06-21

### Added

- Added comment

### Fixed

- Multiple category input was not handled correctly
- Set default None for optional DataLoaderConfig.name

## [6.7.1] - 2024-06-21

### Added

- Add optional name property to DataLoaderConfig

### Changed

- Sentence transformers 3.0 bump
- Updated included direcotries

## [6.5.6] - 2024-06-20

### Changed

- Using our internal publishing tool in conjunction with CPina
- Replace typing module with beartype to support deprecated usage
- Update mongo lib usage (upsert)

### Removed

- Removed tag overwrite

## [6.5.5] - 2024-06-17

### Fixed

- Video #12

## [6.5.3] - 2024-06-17

### Fixed

- Video #1
- Video #2
- Video #3
- Video #4
- Video #5
- Video #6
- Video #7
- Video #8
- Video #9
- Video #10

## [6.5.2] - 2024-06-17

### Changed

- Update release flag to trigger pdoc tool update

## [6.5.1] - 2024-06-13

### Fixed

- Pdoc bson issue

## [6.5.0] - 2024-06-13

### Changed

- Create dsl layer over vdb connector
- Change list to sequence and minor fixes

### Fixed

- Fix docstring type mismatch
- Fix copy pastas

## [6.4.0] - 2024-06-07

### Changed

- Updated wording on CONTRIBUTING.md regarding Poetry virtualenv creation
- Weight support for vector sampler
- Unmutable more error prone

## [6.3.0] - 2024-06-06

### Added

- Add _list_search_index_names_from_vdb

### Changed

- Load initial search indices
- Make index config the collection of index creation params

## [6.2.0] - 2024-06-06

### Changed

- Convert timestamp if pandas overthink and parse it as timestamp

## [6.1.0] - 2024-06-04

### Changed

- Create mongo search index via admin api
- Mongo knn (filters + returned fields + radius)
- Generalize query builder and search

### Fixed

- Typealias naming

### Removed

- Remove exlamation and commented alternatives
- Remove query builder
- Remove mongo equality filter

## [6.0.1] - 2024-06-04

### Changed

- WIP

## [6.0.0] - 2024-05-30

### Fixed

- Notebook output
- Nb hack
- Fix merge

## [5.11.0] - 2024-05-30

### Changed

- Nb for hard filtering feature
- Extended hard filter presentation to show full feature set

### Fixed

- RAG nb transformers version
- Notebook last touches

## [5.10.0] - 2024-05-30

### Removed

- Remove relocated doc ref

## [5.8.1] - 2024-05-28

### Added

- Add REDIS_ENCODED_TYPES
- Add TODO on redis encoder

### Changed

- Redis connector
- Redis query builder

### Fixed

- Import order
- Pr requests
- Raise if unindexable schema fields found
- Use protocol 3 redis connection (turn off decoding results)
- Make kwargs optional for pandas read

## [5.8.0] - 2024-05-28

### Added

- Added conclusion at the end of ad notebook

### Changed

- Update notebooks with categorical input changes
- WIP nb
- Stash notebook
- Notebook base
- Notebook v0.1

### Fixed

- Nb progress
- Recency plotter bug with changed now
- Bug in categorical space
- Matlotlib import

## [5.5.2] - 2024-05-27

### Fixed

- Fix notebook contained float in place of int

## [5.5.1] - 2024-05-27

### Fixed

- Fix netflix notebook contained float in place of int
- Fix notebook contained float in place of int

## [5.4.1] - 2024-05-27

### Added

- Support similar with multiple spaces on same field

### Fixed

- Fix if_not_class_get_origin

## [5.4.0] - 2024-05-27

### Changed

- DD ready
- Draft Event Arithmetics Online Implementation DD
- Updated event arithmetics dd
- Adjust number embedding default logic
- Rename __default_vector_input to __default_vector

## [5.3.0] - 2024-05-24

### Added

- Add skeleton code
- Add force push agreement to CONTRIBUTING
- Add mono repo agreements

### Changed

- Persisting batch load output in vdb DD
- Persisting batch output in vdb DD
- Discuss tradeoff
- Rewording inheritance
- Re-add batchvdbconn wrapper class
- Adjust mono and multi repo agreements

### Fixed

- Teddy comment
- Reword inheritance and adjust code sample
- Attribute

### Removed

- Remove redundant method

## [5.2.3] - 2024-05-24

### Fixed

- Notebook recency

## [5.2.2] - 2024-05-23

### Changed

- Update pdoc paths
- Update release flag to trigger pdoc tool update

## [5.2.1] - 2024-05-23

### Fixed

- Merge conflict resolve

## [5.2.0] - 2024-05-23

### Changed

- Resolve comments
- Community notebook arxiv paper search
- Notebook pip command
- Mimetype renderer

### Fixed

- Convert input id to str in parser

### Removed

- Removed log file

## [5.0.0] - 2024-05-23

### Added

- Add score to search results
- Add backward compatibility comment

### Changed

- Support arrays for categorical similarity
- Event arithmetics
- Event arithmetics updated
- Made doc more concrete
- Refactored temperature
- Event_arithmetics research
- Updated notebook text'
- Text
- Enable mimetype renderer
- Signalled dependency in DD
- Type
- Event final touches
- Introduce node data type + rewrite evaluation result store manager
- Introduce admin data and fields
- Rename Knn to KNN
- Rename AdminFields to Header
- Make field and field_data dict in  entity and entity data
- Rename couple of functions
- Admin fields
- Read node data with typevar arg
- Admin fields + add nparray to PythonTypes
- And not -> or
- Nillable -> nullable

### Fixed

- Typing and other minor suggestions
- Restrict types
- None valued FieldData
- Bug - ndarray is class in 3.10

### Removed

- Remove dask parser but remain the improvements
- Remove entity storage usage from vector sampler
- Remove object store and manager
- Remove in memory entity store
- Remove usage of entity store
- Remove entity store manager
- Remove unnecessary cast
- Remove read_node_results interface from storage manager
- Remove comment
- Remove npt.NDArray
- Remove evaluation result store manager

## [4.1.0] - 2024-05-22

### Changed

- Generify App and Executor

## [4.0.1] - 2024-05-20

### Fixed

- Revert number embedding pr

## [3.46.0] - 2024-05-17

### Changed

- Improve number embedding logic

## [3.45.0] - 2024-05-14

### Changed

- Introduce hard filter in dsl
- Update Index docstring

## [3.44.0] - 2024-05-13

### Changed

- Split runnable to data loader and executor
- Use match instead of ifs

## [3.42.0] - 2024-05-13

### Added

- Add the point for no cross platform
- Add a non goal to the list

### Changed

- Dynamic param for limit

### Removed

- Removed batch related code from the repository post migration

## [3.41.1] - 2024-05-09

### Added

- Add superlinked registry
- Add one-pager for the initial data load
- Add a sentence based on a comment
- Add issues and estimate based on FAI-1835
- Address comments
- Add the point for no cross platform

### Changed

- Filters to be `ComparisonOperation` in `KnnSearchParams`
- Save
- Rework to align with the requirements
- WIP benchmarking nb
- Performance nb skeleteon
- Moved notebook to research

### Fixed

- Fix comments
- Update RELEASE_FLAG

### Removed

- Remove unnecessary base exception class

## [3.41.0] - 2024-05-09

### Added

- Add in memory persistence capability

### Changed

- Inmemory - wip
- InMemoryVDBConnector
- Rename in memory vdb connector

### Fixed

- Resolve merge conflicts
- Rename actual_vector to comparison_vector_field

## [3.40.0] - 2024-05-07

### Changed

- Inner Enum for CustomSpace Agg strategy

## [3.39.1] - 2024-05-06

### Changed

- Custom space showcase agg norm strategies
- Cleared leftover change
- Notebook empty cells

### Fixed

- Recency embedding to use correct negative_filter logic

## [3.39.0] - 2024-05-06

### Added

- Add radius + filters
- Add index_node to dag

### Changed

- Index creation enums
- Make _get_schema_fields Sequence
- StorageManager.create_search_index, drop_search_index, knn_search, write_parsed_schema_field, write_node_results
- StorageManager read
- Rename schema_name to schema_id in EntityId
- Group knn search inputs
- Use regex instead of string ops
- Arithmetics - aggregation
- Modify recency inverse embedding
- Change how we handle recency embedding input

### Fixed

- Wrong return stmt of knn
- Move DistanceMetric
- Renames
- Rename metadata to node data
- Write node result - too many args

### Removed

- Remove node_id from base fields
- Remove extract from field name
- Remove naming with 'primitive'

## [3.38.0] - 2024-05-02

### Added

- Added TODO

### Changed

- Wip hard filter support
- Hard filter support dd
- Update hard_filter_support.md
- INMEMORY_PUT_CHUNK_SIZE as env var

### Fixed

- Rag notebook banner + transformers version

## [3.37.2] - 2024-04-30

### Changed

- Result to_df docstring
- Rename to_df to to_pandas

### Fixed

- Bug in online node casuing e comm nb fail

## [3.37.1] - 2024-04-29

### Added

- Added warning about llama2 transformers bug

## [3.36.0] - 2024-04-26

### Added

- Add assert to each node type

### Changed

- Check list len

### Fixed

- Is_root logic
- Merge conflict

## [3.35.2] - 2024-04-25

### Added

- Add app id for object reader and writer

## [3.35.1] - 2024-04-25

### Fixed

- Small naming issue and parameter
- RAG notebook after bugfix

## [3.35.0] - 2024-04-25

### Changed

- Implement is_root property

## [3.34.1] - 2024-04-25

### Fixed

- Comments
- Visibility of functions

## [3.34.0] - 2024-04-25

### Changed

- Resolve comments

## [3.33.0] - 2024-04-25

### Added

- Add blob field data type
- Add headers
- Add persistable dict to in memory storages
- Add entity storage to the persist and restore methods

### Changed

- Vdb connector
- Clean up TODO questions
- WIP: Rag fixing
- Vector sampler fix
- Nb
- Reverted uninentional notebook changes
- Revert non related file changes from merge
- Number similarity
- Merge conflict
- Nb fix
- Vector sampler chunk support
- Docstring param order

### Fixed

- Dd-compliance
- EntityId.schema_name, FieldData validation call
- Rename Field.type_ to data_type
- User acquisiton umap install in colab
- Merge conflicts

### Removed

- Removed hr notebook
- Remove redundant mocks

## [3.32.0] - 2024-04-24

### Changed

- Renamed param(s)

### Fixed

- NOTICE generation
- Too many arguments

## [3.31.0] - 2024-04-24

### Added

- Add node caching by its id
- Add a helper method to check number of nodes

### Changed

- None handling

### Fixed

- Dsl multilabel
- Method naming

## [3.29.2] - 2024-04-23

### Added

- Added TODO
- Added missint __init__.py files to multiple modules

### Changed

- More immutable more brevity
- Immutable
- Introduce ParentResults
- Updated CONTRIBUTING.md with Tox setup instructions
- Updated link to Tox DD instead of PR in CONTRIBUTING.md

### Fixed

- Query vector creation
- Base chunking
- ON evaluate_singles - sequence instead of list
- Attr name

### Removed

- Removed superlinked/__init__.py

## [3.29.1] - 2024-04-19

### Changed

- Multilabel categorical similarity embedding

### Fixed

- Notebooks should now install superlinked with the interactive extra
- Lowered numpy dependency requirement for 1.25.2

## [3.28.0] - 2024-04-17

### Added

- Add number embedding
- Add batchembedding base class
- Add docstring, abc
- Add param

### Changed

- Number embedding
- Debug
- Use vectorudt
- Enable pyarrow for serialization
- Merge main
- Batch custom node
- Assert df writing

### Fixed

- Downgraded pandas to 2.0.3
- Inheritance

## [3.27.0] - 2024-04-17

### Added

- Add normalization to node id

### Changed

- Order index parents
- Wip: tox is now executable, includes python 3.10, 3.11, 3.12
- Updated PYPI_README.md with the correct python version

### Fixed

- Rephrase a few parts of the dd and resolve comments

### Removed

- Remove persistence params and resolve merge issues
- Removed commend from tox.ini

## [3.26.0] - 2024-04-17

### Changed

- Introduce embedding base class
- Vector arithmetics dd with questions
- Vector arithmetics dd -answered first 2 questions
- Vector arithmetics dd styling
- Vector arithmetics dd - Introduce Aggregation Strategies
- Vector arithmetics dd - future refactors
- Vector arithmetics aggregation based on discussion with Teddy and Mor
- Normalization without aggregation strategies

### Fixed

- Fix __eq__ definition

## [3.23.0] - 2024-04-11

### Changed

- Sunglasses to category-4
- Leftover dev code
- Vector sampler WIP
- Vector sampler feature nb + repr and str methods
- Bumped python version to >=3.10
- Clarified python version in PYPI_README.md
- Similar number and categorical to allow no similar clause
- ENG-1701: TextSimilaritySpace default should be full 0 vector

### Fixed

- Exacted python version further in .python-version
- Downgraded python version from 3.11.7 to 3.11.5
- Fixed find and replace error
- Fixed find and replace errors

## [3.22.0] - 2024-04-10

### Added

- Add node id hashing
- Add proper node ids
- Add dd about the deterministic node ids
- Add alternatives to the doc
- Add tickets to dd
- Add pr guidelines to have clear expectations
- Add info on where to find code owners
- Add info on design docs to contributing

### Changed

- Rework how the string and hash created
- Change parent identification in hash
- Small rework due to the comments
- Changes in DD due to the discussions
- Minor changes in deterministic id dd
- Categorical embedding feature nb
- Custom space feature notebook
- Categorical embedding clearing
- Daniels comments
- Update CODEOWNERS to always have a single owner of a module
- Organize docs to distinc categories to allow fine-graned ownership
- Adjust codeowners to ogranized docs folder

### Fixed

- Fix weighted implementation
- Child-parent misunderstanding

## [3.21.0] - 2024-04-08

### Added

- Add categorical embedding
- Add cat similarity
- Add is_query param

### Changed

- Pull main
- Merge batch nodes branch
- Merge ft branch
- Resolve clashing method names
- Merge main
- Use encoding from embedding
- Reinsert node_id param
- Use udf for embedding
- Undo method name change
- Use vectorudt
- Vector arithmetics dsl

### Fixed

- Assertion
- Merge conflicts
- Path
- Method signature

### Removed

- Remove redundant docstring

## [3.20.0] - 2024-04-05

### Added

- Added communication section, to disambiguate communication ; added section regarding decoupling with git history retention

### Changed

- Categorical space docstring + other similarity bool feature
- Dag and its creation
- Events in dag
- Dag - final touches
- Pr changes - add more detail to dag documentation
- Dag and online_schema_dag documentations

### Fixed

- Property added for non mutable parameter

### Removed

- Remove _get_node from node impls and add to node
- Remove _space_field_set init from space impls and add to base space
- Remove "innate"

## [3.18.1] - 2024-04-04

### Changed

- ENG-1503: limit and radius to be used as params

## [3.18.0] - 2024-04-04

### Added

- Add BatchRecencyEmbeddingNode
- Add exec context to batchdag run
- Add context
- Add recency changes

### Changed

- Batch recency embedding
- Traversing, vector type
- Remoe unimplemented node
- Merge main
- Try diff traversal approach
- Merge traverse
- Recency embedding
- Separate now function
- Schemafieldnode
- Make super first call
- Simplify df writer
- Concatenation node
- Modify now logic in context
- Merge conflicts
- Resolve conflicting schemas
- Merge base branch
- Transform implementation
- Merge ft branch

### Fixed

- Default value
- Merge conflict
- Traverse
- Match case in df writer
- Commit msg
- Find_root
- Find root
- Isinstance
- Traversal
- Instance attributes
- Comments
- Context
- Df assignment
- Resolve conflict
- Fix var name
- Param name
- Merge conflicts
- Pr comments
- Index attr
- Merge
- Lookup schema
- Repo structure
- Merge main
- Function call
- Index node
- Syntax
- Param
- Index node transform
- Variable name

### Removed

- Remove set df
- Remove set_df method
- Remove set method
- Remove redundant init param

## [3.17.0] - 2024-04-03

### Added

- Added initial version of batch decoupling design doc
- Added vector arithmetics info

### Changed

- Static node and online_node mapping
- Fleshed out release plan
- Custom space

## [3.16.0] - 2024-03-28

### Changed

- Minor chunking adjustments
- Chunking split parameters are now parametrizable
- Updated docstring

## [3.15.1] - 2024-03-28

### Fixed

- Hotfix for excluding batch from the published repo
- Modified release flag to trigger a release

## [3.15.0] - 2024-03-28

### Removed

- Remove slow loading warning from examples

## [3.14.4] - 2024-03-28

### Fixed

- Constant-node not handled in batching

## [3.14.3] - 2024-03-28

### Changed

- Move query context check to evaluate
- Load_single_result to load_stored_result

### Fixed

- Modifying release flag, to trigger a new release

## [3.14.1] - 2024-03-26

### Added

- Added default aggregation and normalisation
- Added DSL
- Added query example to DSL in custom space

### Changed

- Custom space + fix space adding DD
- Wording ambigouity removed
- Vector SchemaField extended

### Fixed

- Adjust vector arithmetics DD to recent agreements on query vectors

## [3.14.0] - 2024-03-26

### Added

- Add py.typed

### Changed

- Categorical node to work
- Handle uneven chunk sizes
- Sentence transformer batching dd
- Update batching dd with chunking details
- Update batching dd with more chunking details
- Rename category to category_input
- Renamed files with underscores

### Fixed

- Batch is now under superlinked but excluded from the wheel via Poetry
- Imports for batch now reflect the new module location

### Removed

- Remove deployment directory and other tooling that connected to that

## [3.12.0] - 2024-03-25

### Added

- Add py.typed

## [3.11.0] - 2024-03-25

### Added

- Add strict version handling to semantic-release and failure notification to build

### Changed

- Different chunking logic
- Basic CategoricalSimilaritySpace
- Updated commit message for OSS project sync
- Executor pulls data from correct location
- Resolve comments

### Fixed

- Webhook URL
- Fix types and path logic
- Deploy.py should now show the output line by line not all at once when the subprocess exits
- Modifying release flag, to trigger a new release

## [3.8.0] - 2024-03-17

### Added

- Add instructions about pip and python version

### Changed

- Feature notebooks

## [3.7.0] - 2024-03-16

### Changed

- Adjust copy on the notebooks

### Removed

- Remove unintentional character

## [3.6.0] - 2024-03-15

### Added

- Add example for recency
- Add id field inport

### Changed

- Move example notebooks under feature dir
- Unify naming in internal snippets
- Try rendering
- Plot rendering
- Update notebook metadata to trigger a release
- Rerun to have rendered graphs

### Fixed

- Move import to code section in notebook
- Save charts locally
- Run fix python
- Run notebook
- Pip command missing a _

### Removed

- Remove numbers from snippets
- Remove numbers and number based references of snippets
- Remove snippet numbers from snippet docs

## [3.5.0] - 2024-03-14

### Added

- Add weight to with_vector query

### Changed

- Use nowstrategy in executor

## [3.4.0] - 2024-03-14

### Removed

- Removed irrelevant comment ; fixed grammatical error

## [3.3.0] - 2024-03-14

### Added

- Add inject as optional dep

### Changed

- Separate fastapi from dsl
- Revamp executor
- Resolve comments
- Final comment resolving

### Fixed

- Comments and dependency

## [3.2.1] - 2024-03-14

### Changed

- Replaced all occurrences of superlinked-alpha with superlinked

### Removed

- Remove depricated import of Sequence

## [3.2.0] - 2024-03-14

### Added

- Add deps back
- Add space observability m2 dd
- Add a missing link
- Add outcome of the dump vdb question
- Add gyuris idea on how to name spaces

### Changed

- Separate batch from framework
- Separate batch, remove deps
- Redesign the dsl part and add brainstorming to interface
- Renaming documents

### Fixed

- Merge conflict
- Rename draw to plot for better understanding

## [3.1.0] - 2024-03-13

### Fixed

- Bad merge conflict resolution

## [3.0.0] - 2024-03-13

### Added

- Add TODO comments with ticket refs
- Add nr of id fields to err msg
- Add is_none_valid to single item type check
- Add licence to TypeValidator
- Add docstring to TypeValidator

### Changed

- Use superlinked from pypi and add as dependency
- TypeValidator
- Introduce dynamic typechecker, beartype
- Annotate dict type
- Move beartype to TypeValidator
- Update notebooks with mandatory IdField

### Fixed

- Make id mandatory for schema and event schema
- Validate chunking input
- Validate index input
- Validate inmemorysource input
- Validate inmemoryexecutor init inputs
- Validate query init inputs
- Validate query input types
- Type vs typealias in TypeValidator
- Misplaced InvalidTypeException
- Validate_single_item_type type_ signiture
- Check id in schema only through the validator
- Move init validation from subclass to executor
- Inconsistent use of spec=Param and Param
- Use TypeError instead of InvalidTypeException
- Annotate lists and dicts for beartype
- IdField check with issubclass

### Removed

- Remove unnecessary function declarations from query
- Remove unnecessary var declaration

## [2.37.0] - 2024-03-12

### Changed

- Automatically publish package; update install instructions in Alpha

### Fixed

- Fixed broken links

### Removed

- Removed markdown cell about GITHUB_TOKEN

## [2.35.0] - 2024-03-12

### Added

- Add comments to the example in the PYPI_README

### Changed

- Update PYPI_README with running example
- Refactor references names to start with the use

### Fixed

- Revert prepare-examples for now until a wheel is released

## [2.33.2] - 2024-03-11

### Fixed

- Depend all jobs on check

## [2.33.0] - 2024-03-11

### Changed

- Included NOTICE in the dist packages
- Initial implementation of wheel build from Miniprod cli

### Fixed

- Import os

### Removed

- Remove unnecessary job

## [2.32.5] - 2024-03-11

### Fixed

- Bumped numpy version from 1.21.1 to 1.22.4

## [2.32.1] - 2024-03-08

### Fixed

- Nb env var handling
- Nb json reading nrows handling
- Nb

## [2.32.0] - 2024-03-08

### Changed

- Updated the value of N_ROWS as per discussion with Mor
- Rename env var in nbs

### Fixed

- Cast env var in nbs
- Interactive extra now should contain everything installed inside notebooks

## [2.31.0] - 2024-03-08

### Changed

- Recency_plotter to be able to use context now

## [2.30.0] - 2024-03-08

### Changed

- Replaced if - in construct with match - case

## [2.29.0] - 2024-03-07

### Changed

- Nb related stuff to contributing
- Minor change
- Improve negative filter docstring for recency space

### Fixed

- Type
- Fix ambigous wording
- Eng-1455-recency-space-doesnt-realise-it-is-running-with-milisecond

### Removed

- Removed false concept regarding default value handling

## [2.28.0] - 2024-03-07

### Added

- Add names to dockerfile steps

### Changed

- Make docker images smaller
- Use alpine for poller
- QueryObj functions to create new entities

### Fixed

- Fixed functional error in validate_config
- Simplified path handling ; added unlikely default value for config

## [2.27.0] - 2024-03-06

### Added

- Add LICENSE
- Added newline to compose.yaml to trigger file filter
- Add ticket numbers for todos

### Changed

- Update poetry build command
- Triggering file filter for miniprod
- Introduced config validation to deploy.py
- Run superlinked in the executor

### Fixed

- Nb textfile source
- Execution order in nbs

### Removed

- Remove release step from manual publish job

## [2.26.0] - 2024-03-04

### Changed

- Merge

## [2.25.0] - 2024-03-04

### Added

- Add dummy rest generation

### Changed

- Renamed nbs
- Change default handling
- Extract path method and extract models
- Refactor endpoint creation
- Improved warning message
- Warning message

### Fixed

- Notebook float int bug
- Fix profiler to run with all examples
- Nb install update
- Poetry env numpy version
- Long line comment

### Removed

- Remove inflection
- Remove in memory inheritance
- Remove in memory source instantiation from rest source

## [2.24.0] - 2024-02-28

### Changed

- Introduce batches for inmemorysource put
- RAG notebook
- Other notebook minor beautifications and fixes
- Use smaller LLama model
- Adjusted CONTRIBUTING.md to utilize extras instead of optional dependency groups

### Fixed

- Clarified NOTE in CONTRIBUTING.md
- Renamed notebook extras to interactive

## [2.23.3] - 2024-02-27

### Added

- Add missing GH_TOKEN

## [2.23.2] - 2024-02-27

### Fixed

- New version bump should come before the wheel build

## [2.23.1] - 2024-02-26

### Fixed

- Semantic-release is not needed for build

## [2.23.0] - 2024-02-26

### Added

- Added jupyter update pip step
- Add conventional commit checking git hook
- Add df writer

### Changed

- ENG-1499 Refactor JsonUtil (#201)
- Separate build step into its own job
- Updated file filters to include the project anchor changes on miniprod

### Fixed

- Nb
- Import cell error
- Ipywidgets warning
- Fixed file-filters.yml
- Fixed file-filters.yml anchor usage before assignment
- Doctrings and imports
- Transform
- Call transform
- Class and method names

### Removed

- Remove ont
- Remove import

## [2.22.0] - 2024-02-22

### Changed

- Update Profiling DD with results
- Final touches

### Fixed

- Nb import cell
- Fixed commit

## [2.21.0] - 2024-02-22

### Changed

- Validate parser input mapping

### Fixed

- Void validate

## [2.20.0] - 2024-02-21

### Changed

- User acq notebook + docs: bullepoint desc to nbs
- Check if queried space is in the index

## [2.19.0] - 2024-02-21

### Added

- Add local polling option to miniprod
- Add missing types
- Add comment on why notebook deps are needed for miniprod

### Changed

- Replace list with ndarray in vector for performance
- Replace list with ndarray in VectorField
- Final touches on RecSys nb
- Leftover nb change
- Parse config location with importlib
- Create download_file() abstract method in ResourceHandler

### Fixed

- Recsys nb comments
- PR comments
- Poller main path in Dockerfile
- Install every dependency for local venv

### Removed

- Remove unnecessary comments
- Remove muda comment

## [2.17.4] - 2024-02-20

### Changed

- Perf opt for json path parsing
- Use dict in JsonUtil and return Json

### Fixed

- Adapted Miniprod to Poetry

## [2.17.2] - 2024-02-19

### Fixed

- Temporarily building with fat virtualenv

## [2.17.1] - 2024-02-19

### Added

- Added caching for Poetry environment
- Added missing key runs-on
- Added --no-root flag to all poetry install invocations

### Changed

- Adapting toolchain to Poetry
- Cherry-picked .pre-commit-config.yaml
- Commented out package update step of pre-commit, TBD how to proceed
- Renamed groups executor and poller to deployment-executor deployment-poller respectively
- Updated CONTRIBUTING.md to reflect changes introduced by Poetry
- Incorporated PR feedback into CONTRIBUTING.md

### Fixed

- Fixed job run stage
- Cache path was broken
- Poetry managed venv is now cached
- Poetryfied build and release tools
- Fixed erroneous virtualenv activation in deploy stage
- Bugfix in deploy

### Removed

- Removed unnecessary pip upgrade
- Removed commented out pre-commit-config section regarding package updates on pre-commit trigger

## [2.17.0] - 2024-02-19

### Added

- Address PR comments regarding app_location parsing
- Add default value for config.yaml
- Add s3n support to poller
- Add impl details and scope to the observability doc

### Changed

- Profiling Approach
- Recsys notebook, fix: nb text width
- Move logging config to ini file
- Upgrade paths-filter version
- Update CONTRIBUTING.md with pre-commit related updates
- Read poller configs from json instead of baked in global wars
- User acquisition notebook
- Import cell
- Perf opt for vector length calc
- Split up milestone 3

### Fixed

- Import at the beginning of notebooks
- Recsys nb minor nits
- Venv creation do not force python reinstall
- Correct path for logging config and stdout
- Dockerfile update to fit the module structure
- Magic strings eliminated, config from argument, fix download method, loglevel increased to INFO
- Migrate deploy.py to compose v2 syntax
- Path-filter exclusion does not work on dorny
- Path-filter to use ${{}} syntax for negation
- Make get_bucket_and_path_or_raise() private
- Drop dict magic and use AppLocation instead
- Use ValueError's type instead of __class__ of expected_result; adjust pre-commit config
- Avoid negation in file-filters and use detailed anchors instead
- Move *project under core instead of deploy
- Return more info if the config is invalid
- Use raise_for_status() instead of http 200 for successful response
- Small fixes from comments
- Vector sample adjustment

### Removed

- Removed RAG notebooK

## [2.16.0] - 2024-02-14

### Added

- Add vector sampler class

### Changed

- DefaultNode logic for NumberSpace
- Refactor to align with comments
- Small changes with naming

### Fixed

- Return values for the vector sampler and docs added

## [2.14.2] - 2024-02-12

### Added

- Add similar mode to number similarity space
- Add krisztian-gajdar to CODEOWNERS

### Fixed

- Notebook feedback + WIP: recsys nb
- Fix pr comments
- Align dd with implementation

## [2.14.1] - 2024-02-09

### Fixed

- Altair plotting

## [2.14.0] - 2024-02-09

### Changed

- Basics of REST API structure
- Adjust to rest source concept
- Semantic search notebook

## [2.12.0] - 2024-02-06

### Changed

- .with_vector example in netflix notebook
- Genre altering cell in netflix notebook
- Final touches

### Removed

- Removed empty cell from the end

## [2.11.0] - 2024-02-06

### Added

- Added *.swp to .gitignore
- Added caveats section to dependency management system comparison

### Changed

- Copied comparison document from notion to git
- Checking on other platforms
- Updated design doc for dependency management
- Separated DD and implementation
- Updated dev dependency add as per documentation

### Fixed

- Modify version constraints on altair

### Removed

- Remove obsolete PR instructions and add info about creating a snippet for feature development

## [2.10.0] - 2024-02-06

### Added

- Add missing requirements file to root reqs

### Changed

- Prepare marshal method to accept list of parsed schemas

### Fixed

- Revert large instance
- Decouple different requirements to avoid dependency cycle issues

### Removed

- Remove compensation from code of conduct in favor of role cards

## [2.9.0] - 2024-02-02

### Added

- Add negative filter check for number space

## [2.8.0] - 2024-02-01

### Added

- Add negative filter and rename mode
- Add better better wording to space errors

### Changed

- Extract vector calculations to its own module

### Fixed

- Fixing comments on PR

## [2.7.1] - 2024-02-01

### Added

- Added output

### Fixed

- Fix leftover code
- Sentence_transformers version

## [2.6.0] - 2024-01-31

### Added

- Add OueryFilters

### Changed

- Updated docstrings
- Introduce QueryVectorFactory
- Adjust ParamEvaluator
- Function renaming, opertiontype grouping
- Use newly introduced modules

### Fixed

- Categorical space number space reference

## [2.5.0] - 2024-01-31

### Added

- Add type checking to spaces

### Changed

- Refactor space input validation
- Changes due to pr comments

## [2.4.1] - 2024-01-30

### Added

- Add __init__.py files to fix packaging

### Fixed

- Typing import

## [2.4.0] - 2024-01-30

### Added

- Add batch_data_load endpoint to API
- Add ticket numbers to TODO comments

### Changed

- With Client instead of declaration and close
- Chain operations on dask dataframe
- Avoid magic numbers
- Improve error handling with custom handlers
- Idea
- Vector arithmetics DD
- Updated DD
- Move batch_data_load() to the DataLoaderInterface

### Fixed

- Close Dask client when an exception happens
- Module imports
- Missing fsspec dependency

### Removed

- Remove unnecessary mock magic
- Remove magic string

## [2.3.0] - 2024-01-25

### Added

- Add the how to space DD

### Changed

- Scalar space addition
- Rename scalar space and last touches

### Fixed

- Merge issue on GH

## [2.2.0] - 2024-01-25

### Added

- Add query weighting
- Add proper weighting for nodes

### Changed

- Separate predicates
- Introduce DEFAULT_WEIGHT

### Fixed

- Naming

## [2.1.4] - 2024-01-23

### Changed

- Finalize query execution refactor dd

## [2.1.3] - 2024-01-23

### Added

- Add proper TODO

### Fixed

- Query weighting

## [2.1.2] - 2024-01-19

### Added

- Add all resources from alpha to example/src to compile

### Changed

- Query execution refactor dd
- Update query execution refactor - WIP
- Init code_walk_through md
- Code_walk_through md

### Fixed

- Fix wording

## [2.1.1] - 2024-01-17

### Changed

- Fmt
- Change api response status

### Fixed

- Notebook conflic

## [2.1.0] - 2024-01-17

### Fixed

- Baly executed merge

## [2.0.0] - 2024-01-17

### Added

- Add new DD

### Changed

- Return stored object implementation

### Fixed

- Notebook prints

### Removed

- Remove the default limit
- Remove entitywithmetadata

## [1.11.3] - 2024-01-17

### Added

- Add scenario 5
- Add group by
- Add groupby

### Changed

- Notebook styling
- Restructure API
- Create scenarios for event processing
- Update event process dds
- DagEffect
- Introduce DagMixin
- Pass nodes to online schema dag compiler's init

### Fixed

- Small bugs
- Misspelled persistence
- Rename project_parents_to_dag_effect to project_parents_for_dag_effect
- Rename complete to resolved schema reference
- Pass index to InMemoryDataProcessor
- Deployment and a bad import

### Removed

- Remove unnecessary lambda

## [1.11.2] - 2024-01-16

### Fixed

- Deployment issues

## [1.11.1] - 2024-01-16

### Fixed

- Reqs

## [1.11.0] - 2024-01-16

### Added

- Added init files
- Added epoch print

### Changed

- Moved around properties in recency nodes
- Recency plotting v1
- RecencyPlotter
- Logging
- Epoch print

### Fixed

- Utc timestamps
- Comments on PR
- Rename and PR comments
- Comments, naming, zero div check

## [1.10.1] - 2024-01-15

### Added

- Add missing typization to method args
- Add more missing types

### Changed

- Migrate superlinked-deployment to the superlinked core repo
- Replace typing.Dict with dict
- Import Callable from collections.abc

## [1.10.0] - 2024-01-08

### Added

- Add public API documentation intstructions to CONTRIBUTING
- Add user flow to DD
- Add limit and radius to knn

### Changed

- Update mini deploy DD

### Fixed

- Comments were resolved

## [1.9.0] - 2024-01-05

### Added

- Add fallback load last result
- Add colon to metadata property key
- Add some order clarification to index init

### Changed

- Introduce PersistanceType
- Clean up exceptions
- Create ANs and EANs
- Process event
- Disable multiplying affected schema reference
- Clarify effect grouping
- Rename last to stored

### Fixed

- Working with empty vector
- Pr
- Index parents validation call

## [1.8.1] - 2024-01-04

### Fixed

- Adjust the example preparation step to fix regression on examples folder without files as direct children

## [1.8.0] - 2024-01-03

### Added

- Added table for better comprehension
- Added SimilarNumberSpace
- Added query vector

### Changed

- Scalar space design doc stage 1
- Escape char
- Math formula
- Clarifications
- Updated naming
- Categorical DD
- Updated justification for space separation
- Extended arguments for one-hot encoding
- Small update on binning
- Binning -> categorisation
- Binner + other small mods
- Exact categories to be set, removed binning

### Fixed

- Fixed relative link

### Removed

- Remove alpha assets and files that will be directly managed in the alpha repository

## [1.7.0] - 2023-12-14

### Changed

- Started scalar space doc

## [1.6.0] - 2023-12-13

### Added

- Added warning for weird recency param values

### Fixed

- PeriodTimeParam alone to RecencySpace

## [1.5.0] - 2023-12-13

### Changed

- Concretize types
- Unnecessary cast

### Removed

- Remove pyre

## [1.4.0] - 2023-12-12

### Fixed

- Order of inheritance

## [1.3.0] - 2023-12-12

### Changed

- Project Node parent to schema
- Compile with Node-based projection
- Move length from online to general dag level
- SentenceTransformer init on TEN init

### Removed

- Remove leftover

## [1.2.0] - 2023-12-11

### Changed

- MultipliedSchemaReference
- Make HasMultiplier abstract class

## [1.1.0] - 2023-12-11

### Changed

- Unity enum naming

## [1.0.0] - 2023-12-11

### Added

- Add docstring to all files that will be exposed transitively or directly when using the framework
- Add TODO and adjust data parser init function
- Add docstring to JsonParser
- Add missing docstrings and exclude dsl components that are not exposed to the user directly
- Add docs building to alpha

### Changed

- Comparion operand
- ComparisonFilterNode
- Note agreements around docstrings
- Move period time param to dedicated file for individual exposue in docs
- Adjust superlinked-alpha issue tracking to newest method
- Adjust Gyuri recommendations mostly stylistic difference

### Fixed

- Fix paths for docs builder
- Failed ide renaming in decoratorated function overload

## [0.9.0] - 2023-12-07

### Added

- Add weights to AN
- Add dimension property to Vector
- Add EventSchema to EAN + Effect post_init

### Changed

- Aggregation and event aggregation node
- Make Nodes DefaultNode wherever possible
- OnlineAggregationNode
- OnlineEventAggregationNode

### Fixed

- Pr

## [0.8.0] - 2023-12-07

### Changed

- Port PERF to CODE_OF_CONDUCT
- Post main merge fixes

## [0.7.0] - 2023-12-07

### Changed

- Main merge fixes
- PR comment fixes
- Rename query time override for clarity and add remark
- Rename patched __new__ variable name for consistency
- Minor PR fixes

### Fixed

- Fixes
- Use the same now in all context during the query
- Fix main merge

### Removed

- Remove update/copy as there are alternative functions
- Remove code

## [0.6.0] - 2023-12-05

### Added

- Add override for queries to set exact time
- Add EvaluationResultStoreManager to evaluation

### Changed

- Moved negative_filter to space
- Adjusted example negative_filter usage
- Comment about recency dimensions
- Design doc for the feature
- Executor context with now()
- Inherited init does nothing
- Set line length
- Reminder to fix code copies
- Context changed
- Use new context
- Set query time to now according to DD
- Merge
- EvaluationResultStoreManager
- Persist evaluation result
- Update event_processing

### Fixed

- Past querying had wrong value
- Bug in calculating the now
- Leftover

### Removed

- Removed unnecessary vector dimensions
- Remove unnecessary init

## [0.5.1] - 2023-12-04

### Added

- Add basics for code of conduct

### Changed

- Update READMEs and add development instructions to a dedicated CONTRIBUTING file
- No trailing underscore

### Fixed

- Notebook schema imports
- Import

## [0.5.0] - 2023-11-30

### Changed

- TODO moved

## [0.4.1] - 2023-11-30

### Fixed

- Make schema name part of the vector row key

## [0.4.0] - 2023-11-30

### Changed

- Introduce SchemaFieldBinaryOp
- Introduce Effect
- Move id name generation

## [0.3.0] - 2023-11-30

### Added

- Added docstrings to dsl
- Add proper exception
- Add more clear error text

### Changed

- Docstrings
- App docstring
- Comments
- Separate SchemaObject and schema
- Schema decorator, factory, validator
- IdSchemaObject
- EventSchema
- Reference with generic annotation
- SchemaFieldBinaryOp
- Introduce effect
- Make id mandatory for events
- Modify event json in S6

### Fixed

- Make referenced_schema protected

### Removed

- Removed leftover comment
- Remove leftover
- Remove leftover import

## [0.2.3] - 2023-11-28

### Fixed

- Notebook order
- Reference passing
- None or False

### Removed

- Removed id index

## [0.2.2] - 2023-11-28

### Fixed

- Do not upload artefacts (they are not there yet)

## [0.2.1] - 2023-11-27

### Added

- Add a new line

### Fixed

- Update README.md

### Removed

- Remove space

## [0.2.0] - 2023-11-27

### Added

- Add valiadations to schema creation
- Add comments
- Add option 3
- Add schema projections
- Add implementation
- Add implementation point
- Add suggestion for EventSchema definition
- Add event_schema and reference decorators

### Changed

- New structure + query debug + sensitivity analysis
- Draft dd for S6
- Clarification
- Organize Option 3 diagram
- Organize DAG w/o CN
- Reorganize dd
- Regroup
- Relocate FilterInfo and QueryExecutor
- Introduce ParamEvaluator
- Move dag evaluators
- Separate dag evaluators
- Multi-op query
- Comments + clarification
- Adjust new issue urls on superlinked-alpha
- Reintroduced negative recency notebook example
- Trigger diff

### Fixed

- Id field name
- Semantic release is only in the virtualenv
- Rename variables
- QueryExecutor.update_weights
- Exception name
- In vector aggregate check dim not length
- Notebooks
- Commit actor is not working
- Run release after tagging, to get the proper version
- Recency weighting
- Merge removed z_value
- Order of switches
- Bumping should push tag

### Removed

- Remove leftover
- Removed negative recency example
- Removed leftover

## [0.1.3] - 2023-11-23

### Added

- Add online system design details
- Add combination of previous solutions as option
- Add check to re_weight_vector - ocn
- Add issue templates to superlinked-alpha project

### Changed

- Draft version of the demo production dd
- DD containing my design
- Introduce HasLength interface
- Re-weight vector query-time
- Assign __length on init
- Re-introduce DagEvaluator
- Update alpha contribution docs

### Fixed

- Move to goals
- Relocate HasLength
- Clarification on re-weighting

### Removed

- Remove obsolete parts

## [0.1.1] - 2023-11-21

### Added

- Add section about versioning
- Add examples of tagging
- Added design doc v1

### Changed

- Periodtime, timedelta
- Recency weight + query mode
- Context util is_query
- Started design doc
- PR comments

### Fixed

- Weights + added meaningful outputs
- Wording
- Default param 0.0
- Imports
- Unnecessary files
- Fix gitignore

## [0.1.0] - 2023-11-17

### Added

- Add removed check
- Added notebook results

### Changed

- Rename root module to superlinked
- Netflix notebook
- Gitignore
- Rename
- Dataset publicly available

### Fixed

- Rename filter to predicate
- Rename patches
- Notebook naming and duplication
- Notebook imports for new notebook

### Removed

- Remove DEFAULT_WEIGHT
- Removed changes

## [0.0.12] - 2023-11-13

### Added

- Add normalization
- Add custom filters to EntityFilterMixin

### Changed

- Separate post_init from init in OnlineNode
- Unified id validation in parsers
- SourceLoadMixin
- EntityFilterMixin

### Fixed

- Wasteful instanstiation of SentenceTransformer object
- Dataframe parser checks
- Node
- Mocking new of SentenceTransformer
- PR comments
- Id validation
- Expression is negated
- Naming
- Recency calculation
- Pr

### Removed

- Remove leftover
- Remove post_init from OnlineNode
- Remove unnecessary check
- Remove typeignore
- Remove notebook

## [0.0.10] - 2023-11-13

### Changed

- Check if env/variables are set to avoid weird errors

## [0.0.9] - 2023-11-13

### Added

- Add eof new line
- Add check if whl exists
- Add commit message
- Add limitations and fix simple example
- Add notebook template
- Add template for example notebook and recency combination example
- Add combination demo

### Changed

- Print the branch name
- Run on main only
- Complie examples and update in superlined-alpha repo
- Draft version of demoability poc
- Adjust demoability dd to new findings and sync
- Adjust the combinined example and remove the token
- Replace current version placeholder in example notebook
- Update codeownrers file
- Multiple similar clause with weights
- Rename FieldSet
- Check version and only push examples if it is a main version
- Init venv for check job

### Fixed

- Pr
- Output
- Syntax
- Simple example
- Pr changes
- Raise exception when not all filters are SIMILAR when there is one SIMILAR
- Pass vector id as param
- Step-name

### Removed

- Remove old examples
- Remove token
- Remove results from notebook

## [0.0.8] - 2023-11-09

### Changed

- Switch to superlinked-aplha branch

## [0.0.7] - 2023-11-07

### Added

- Add example for S4

### Changed

- Deployment uses req-dev.txt
- Introduce Entity
- Origin_id

### Fixed

- Source of now
- Make EntityId frozen

### Removed

- Remove default uuid

## [0.0.6] - 2023-11-07

### Changed

- Debug version
- Run on main only
- Check tag push branches too
- Use main branch

### Fixed

- Fetch all history to make versionizing work
- Whl build includes

### Removed

- Remove fetch tags

## [0.0.5] - 2023-11-06

### Changed

- Tags are not checked out by default

## [0.0.4] - 2023-11-06

### Added

- Add Gyuri's v3 version of the library
- Add basic example that seems at least 30% feasible
- Add relevance example
- Add document similarity example
- Add paragraph personalization example
- Add paragraph personalized query scenario and snippet
- Add entre snippet proposal
- Added jsons for usecases
- Add snippets
- Added TODOs
- Add scenario 1 snippet agreements
- Add tools
- Added snippets
- Add initial design doc
- Add docstring for in memory vdb performance
- Add check for optional properties in knn
- Add TODO ticket
- Add dd for separating vdb implementation from connectors
- Add adjusted in_memory_store
- Add design doc for text-similarity-space
- Add +x
- Add playground
- Add dag conversion by composition
- Add 2nd scenario
- Added Id to all schemas
- Added snippet + fixes
- Add scenario#4
- Add pyre as dep.
- Add schema name and filtering for vector storage
- Add assert for the declared schema type as well
- Add chunking
- Add some clarification to the error
- Add comment about the seemingly weird file replacement
- Add build step
- Add hg token to enable gh cli

### Changed

- Adjust to MR
- Adjust similarity to mr
- Proposal for retrieval augmented generation
- Use annotation instead of join in document-similarity
- Expand on the scenarios
- Dag base
- Move json examples to the examples directory
- Adjust the proposal for scenario 1
- Further cleaning
- Reworked examples
- Dag components
- Move around dsl code
- Basic build system
- Python tooling
- Move files
- Publish improved dd for vdbs
- Skeleton for vdb
- Implement knn and filtering for in-memory-vdb
- Use range properly, fix docstring
- Dd for online executor
- Skeleton of online executor components
- Initial online executor
- Query language
- Clean up the app interface
- Adjust dd
- Further iteration on vdb implementation
- Vdb proposal with separated kv store
- Dd with separated store and store_manager classes
- Use subset naming for key_value_filter check
- Use None instead of optional
- Avoid overwriting __eq__
- Thoughts on similarity embeddings
- Implement sentence transformer
- JsonParser with default mapping
- Rename stream
- Vector-topology md
- Move all configs into one config file
- Waiting for vdb modifications
- Use newly introduced StoreManager
- DataFrameParser
- Directory structure
- Move parser module
- Make schema a common component
- Move back parser
- Store type of SchemaField
- New snippet proposals in README.md
- New snippets
- Graph embedding notations upgraded
- Rename S8 and CollaborativeFilteringSpace
- In-memory executor
- Clarify sources
- Print both entity_id and node_id
- Make _schema_fields private
- DD for query weights
- Lib should pull only common deps
- Make weights in evaluator optional
- Rename Datetime class to TImestamp
- Separate dag evaluation from storing logic
- Retrieve subclasses of base class
- Introduce online nodes
- Online node compiler
- ParsedSchemaField-SchemaField composition
- Introduce concatenation node
- Introduce recency node and space
- Period time param
- Default for recency "vectorizer"
- Multiply vector with scalar
- Use query time weights
- List not needed anymore
- Use dataclass instead of tuple
- Make members protected
- Training loop DD
- Design doc
- Design doc feedback incorporated
- Multiple schema field in space definition
- Search by user_id DSL
- Separate ParsedSchema from DataParser
- Clean up SchemaObject
- Serialize ParsedSchema
- Save data
- DataFrameParser marshal
- DataStoreManager -> ObjectStoreManager
- Interface for object store
- Use prefix+suffix not to mask user fields
- Move schema_name out of EntityId
- Wip
- OnlineSchemaDag
- IndexNode
- EvaluationResult
- Filter_index_sources
- Refactor query execution
- Refactor
- ChunkedSstring - WIP
- ChunkingNode
- Adjust scenarios to new chunking logic
- Unify evaluation results
- Introduce FixedNode
- Make evaluate_single protected
- NamedFunctionNode
- Introduce DefaultOnlineNode
- Rename fixed to constant
- Clarified limitations
- Finished doc
- CODEOWNERS
- Move not working examples to docs and fix working examples
- Introduce custom exceptions
- Use correct model name in snippets
- Use underscore separation for file names markdown
- Ignore some already known issue
- Move common initialisations to common class
- Separate checking for supported ops and parsing info needed for similarity query
- Change deprecated setup.py to the toml based build definition
- Setup python environment
- Release wheel

### Fixed

- Embedding current time in paragraph-recency snippet
- Moved and renamed preprocessors key
- Idea to gitignore
- Fixed comment
- Consistency Balazs comments
- Rag definition
- Mr
- Instatiate new entities for every vdb
- Mr changes
- Notebook is not part of the lib, framework is
- Use future annotations so no string typing is necessary
- Typing
- Proper isinstance in online executor
- Typing and minor fixes
- MR discussions
- Df parser types
- Naming
- TODO added
- Imports in data parser after refactor
- Image schema stuff
- Nodes array
- No need for query_weight
- S10 to work with in sample image
- Gyuri comments
- Data is a list
- Fix example
- Mr fixes
- Return unpacked row_id from storage as entity id
- Id is mandatory
- Protected/private
- Function place
- Small changes
- IdField
- Renamed DD
- Space duplication
- Use the proper model
- For into comprehension
- Names
- Fix assert
- Mate the PR providing multiple schema indices with the query by id PR
- PR comments
- Pr
- Chunking defaults
- Merge error
- PR fixes
- Fix references in snippets
- Resolve merge issues
- PR comments on mock return values
- Checkout first
- Rename files
- Rename job name
- Move jobs to the same file
- Change condition
- Release version

### Removed

- Remove previous project
- Remove previously ignored files
- Remove embed function
- Removed old model used only for reference
- Remove unnecessary dict update
- Removed Optional
- Remove to-be-deprecated type hints
- Remove TODO
- Removed TODO
- Removed user instantiated schema
- Remove unnecessary import
- Remove unnecessary file
- Removed comments
- Remove OnlineDag
- Remove unnecessary call
- Remove extra field

[33.3.0]: https://github.com/superlinked/superlinked/compare/v33.2.0..v33.3.0
[33.0.0]: https://github.com/superlinked/superlinked/compare/v32.4.0..v33.0.0
[32.4.0]: https://github.com/superlinked/superlinked/compare/v32.3.0..v32.4.0
[32.3.0]: https://github.com/superlinked/superlinked/compare/v32.2.1..v32.3.0
[32.2.1]: https://github.com/superlinked/superlinked/compare/v32.2.0..v32.2.1
[32.2.0]: https://github.com/superlinked/superlinked/compare/v32.1.0..v32.2.0
[32.1.0]: https://github.com/superlinked/superlinked/compare/v32.0.0..v32.1.0
[32.0.0]: https://github.com/superlinked/superlinked/compare/v31.4.1..v32.0.0
[31.4.1]: https://github.com/superlinked/superlinked/compare/v31.4.0..v31.4.1
[31.4.0]: https://github.com/superlinked/superlinked/compare/v31.3.0..v31.4.0
[31.3.0]: https://github.com/superlinked/superlinked/compare/v31.2.4..v31.3.0
[31.2.4]: https://github.com/superlinked/superlinked/compare/v31.2.3..v31.2.4
[31.2.3]: https://github.com/superlinked/superlinked/compare/v31.2.2..v31.2.3
[31.2.2]: https://github.com/superlinked/superlinked/compare/v31.2.1..v31.2.2
[31.2.1]: https://github.com/superlinked/superlinked/compare/v31.2.0..v31.2.1
[31.2.0]: https://github.com/superlinked/superlinked/compare/v31.1.1..v31.2.0
[31.1.0]: https://github.com/superlinked/superlinked/compare/v31.0.0..v31.1.0
[30.2.0]: https://github.com/superlinked/superlinked/compare/v30.1.0..v30.2.0
[30.1.0]: https://github.com/superlinked/superlinked/compare/v30.0.0..v30.1.0
[30.0.0]: https://github.com/superlinked/superlinked/compare/v29.7.0..v30.0.0
[29.6.5]: https://github.com/superlinked/superlinked/compare/v29.6.4..v29.6.5
[29.6.4]: https://github.com/superlinked/superlinked/compare/v29.6.3..v29.6.4
[29.6.2]: https://github.com/superlinked/superlinked/compare/v29.6.1..v29.6.2
[29.6.1]: https://github.com/superlinked/superlinked/compare/v29.6.0..v29.6.1
[29.6.0]: https://github.com/superlinked/superlinked/compare/v29.5.0..v29.6.0
[29.5.0]: https://github.com/superlinked/superlinked/compare/v29.4.0..v29.5.0
[29.4.0]: https://github.com/superlinked/superlinked/compare/v29.3.0..v29.4.0
[29.3.0]: https://github.com/superlinked/superlinked/compare/v29.2.1..v29.3.0
[29.2.1]: https://github.com/superlinked/superlinked/compare/v29.2.0..v29.2.1
[29.1.0]: https://github.com/superlinked/superlinked/compare/v29.0.0..v29.1.0
[28.12.0]: https://github.com/superlinked/superlinked/compare/v28.11.0..v28.12.0
[28.11.0]: https://github.com/superlinked/superlinked/compare/v28.10.0..v28.11.0
[28.10.0]: https://github.com/superlinked/superlinked/compare/v28.9.0..v28.10.0
[28.9.0]: https://github.com/superlinked/superlinked/compare/v28.8.2..v28.9.0
[28.8.2]: https://github.com/superlinked/superlinked/compare/v28.8.1..v28.8.2
[28.8.1]: https://github.com/superlinked/superlinked/compare/v28.8.0..v28.8.1
[28.8.0]: https://github.com/superlinked/superlinked/compare/v28.7.0..v28.8.0
[28.7.0]: https://github.com/superlinked/superlinked/compare/v28.6.0..v28.7.0
[28.6.0]: https://github.com/superlinked/superlinked/compare/v28.5.1..v28.6.0
[28.5.1]: https://github.com/superlinked/superlinked/compare/v28.5.0..v28.5.1
[28.5.0]: https://github.com/superlinked/superlinked/compare/v28.4.1..v28.5.0
[28.4.1]: https://github.com/superlinked/superlinked/compare/v28.4.0..v28.4.1
[28.4.0]: https://github.com/superlinked/superlinked/compare/v28.3.1..v28.4.0
[28.2.0]: https://github.com/superlinked/superlinked/compare/v28.1.5..v28.2.0
[28.1.5]: https://github.com/superlinked/superlinked/compare/v28.1.4..v28.1.5
[28.1.4]: https://github.com/superlinked/superlinked/compare/v28.1.3..v28.1.4
[28.1.3]: https://github.com/superlinked/superlinked/compare/v28.1.2..v28.1.3
[28.1.2]: https://github.com/superlinked/superlinked/compare/v28.1.1..v28.1.2
[28.1.0]: https://github.com/superlinked/superlinked/compare/v28.0.0..v28.1.0
[28.0.0]: https://github.com/superlinked/superlinked/compare/v27.6.1..v28.0.0
[27.6.1]: https://github.com/superlinked/superlinked/compare/v27.6.0..v27.6.1
[27.6.0]: https://github.com/superlinked/superlinked/compare/v27.5.0..v27.6.0
[27.5.0]: https://github.com/superlinked/superlinked/compare/v27.4.0..v27.5.0
[27.4.0]: https://github.com/superlinked/superlinked/compare/v27.3.0..v27.4.0
[27.3.0]: https://github.com/superlinked/superlinked/compare/v27.2.2..v27.3.0
[27.2.2]: https://github.com/superlinked/superlinked/compare/v27.2.1..v27.2.2
[27.2.1]: https://github.com/superlinked/superlinked/compare/v27.2.0..v27.2.1
[27.2.0]: https://github.com/superlinked/superlinked/compare/v27.1.0..v27.2.0
[27.1.0]: https://github.com/superlinked/superlinked/compare/v27.0.0..v27.1.0
[27.0.0]: https://github.com/superlinked/superlinked/compare/v26.0.0..v27.0.0
[26.0.0]: https://github.com/superlinked/superlinked/compare/v25.1.0..v26.0.0
[25.0.0]: https://github.com/superlinked/superlinked/compare/v24.0.0..v25.0.0
[24.0.0]: https://github.com/superlinked/superlinked/compare/v23.9.0..v24.0.0
[23.9.0]: https://github.com/superlinked/superlinked/compare/v23.8.0..v23.9.0
[23.8.0]: https://github.com/superlinked/superlinked/compare/v23.7.0..v23.8.0
[23.7.0]: https://github.com/superlinked/superlinked/compare/v23.6.1..v23.7.0
[23.6.1]: https://github.com/superlinked/superlinked/compare/v23.6.0..v23.6.1
[23.6.0]: https://github.com/superlinked/superlinked/compare/v23.5.0..v23.6.0
[23.5.0]: https://github.com/superlinked/superlinked/compare/v23.4.0..v23.5.0
[23.4.0]: https://github.com/superlinked/superlinked/compare/v23.3.0..v23.4.0
[23.3.0]: https://github.com/superlinked/superlinked/compare/v23.2.1..v23.3.0
[23.2.1]: https://github.com/superlinked/superlinked/compare/v23.2.0..v23.2.1
[23.2.0]: https://github.com/superlinked/superlinked/compare/v23.1.0..v23.2.0
[23.1.0]: https://github.com/superlinked/superlinked/compare/v23.0.1..v23.1.0
[23.0.0]: https://github.com/superlinked/superlinked/compare/v22.17.1..v23.0.0
[22.17.1]: https://github.com/superlinked/superlinked/compare/v22.17.0..v22.17.1
[22.17.0]: https://github.com/superlinked/superlinked/compare/v22.16.1..v22.17.0
[22.16.1]: https://github.com/superlinked/superlinked/compare/v22.16.0..v22.16.1
[22.16.0]: https://github.com/superlinked/superlinked/compare/v22.15.2..v22.16.0
[22.15.2]: https://github.com/superlinked/superlinked/compare/v22.15.1..v22.15.2
[22.15.1]: https://github.com/superlinked/superlinked/compare/v22.15.0..v22.15.1
[22.15.0]: https://github.com/superlinked/superlinked/compare/v22.14.1..v22.15.0
[22.14.1]: https://github.com/superlinked/superlinked/compare/v22.14.0..v22.14.1
[22.13.1]: https://github.com/superlinked/superlinked/compare/v22.13.0..v22.13.1
[22.13.0]: https://github.com/superlinked/superlinked/compare/v22.12.0..v22.13.0
[22.12.0]: https://github.com/superlinked/superlinked/compare/v22.11.0..v22.12.0
[22.11.0]: https://github.com/superlinked/superlinked/compare/v22.10.0..v22.11.0
[22.10.0]: https://github.com/superlinked/superlinked/compare/v22.9.0..v22.10.0
[22.8.0]: https://github.com/superlinked/superlinked/compare/v22.7.1..v22.8.0
[22.7.0]: https://github.com/superlinked/superlinked/compare/v22.6.4..v22.7.0
[22.6.4]: https://github.com/superlinked/superlinked/compare/v22.6.3..v22.6.4
[22.6.2]: https://github.com/superlinked/superlinked/compare/v22.6.1..v22.6.2
[22.6.1]: https://github.com/superlinked/superlinked/compare/v22.6.0..v22.6.1
[22.6.0]: https://github.com/superlinked/superlinked/compare/v22.5.0..v22.6.0
[22.5.0]: https://github.com/superlinked/superlinked/compare/v22.4.0..v22.5.0
[22.4.0]: https://github.com/superlinked/superlinked/compare/v22.3.2..v22.4.0
[22.3.1]: https://github.com/superlinked/superlinked/compare/v22.3.0..v22.3.1
[22.3.0]: https://github.com/superlinked/superlinked/compare/v22.2.0..v22.3.0
[22.2.0]: https://github.com/superlinked/superlinked/compare/v22.1.2..v22.2.0
[22.1.2]: https://github.com/superlinked/superlinked/compare/v22.1.1..v22.1.2
[22.1.1]: https://github.com/superlinked/superlinked/compare/v22.1.0..v22.1.1
[22.1.0]: https://github.com/superlinked/superlinked/compare/v22.0.1..v22.1.0
[22.0.1]: https://github.com/superlinked/superlinked/compare/v22.0.0..v22.0.1
[22.0.0]: https://github.com/superlinked/superlinked/compare/v21.3.1..v22.0.0
[21.3.1]: https://github.com/superlinked/superlinked/compare/v21.3.0..v21.3.1
[21.3.0]: https://github.com/superlinked/superlinked/compare/v21.2.0..v21.3.0
[21.1.0]: https://github.com/superlinked/superlinked/compare/v21.0.0..v21.1.0
[21.0.0]: https://github.com/superlinked/superlinked/compare/v20.5.0..v21.0.0
[20.5.0]: https://github.com/superlinked/superlinked/compare/v20.4.0..v20.5.0
[20.4.0]: https://github.com/superlinked/superlinked/compare/v20.3.2..v20.4.0
[20.3.2]: https://github.com/superlinked/superlinked/compare/v20.3.1..v20.3.2
[20.3.1]: https://github.com/superlinked/superlinked/compare/v20.3.0..v20.3.1
[20.2.0]: https://github.com/superlinked/superlinked/compare/v20.1.1..v20.2.0
[20.1.1]: https://github.com/superlinked/superlinked/compare/v20.1.0..v20.1.1
[20.1.0]: https://github.com/superlinked/superlinked/compare/v20.0.0..v20.1.0
[20.0.0]: https://github.com/superlinked/superlinked/compare/v19.22.0..v20.0.0
[19.22.0]: https://github.com/superlinked/superlinked/compare/v19.21.2..v19.22.0
[19.21.2]: https://github.com/superlinked/superlinked/compare/v19.21.1..v19.21.2
[19.21.1]: https://github.com/superlinked/superlinked/compare/v19.21.0..v19.21.1
[19.21.0]: https://github.com/superlinked/superlinked/compare/v19.20.0..v19.21.0
[19.19.1]: https://github.com/superlinked/superlinked/compare/v19.19.0..v19.19.1
[19.18.0]: https://github.com/superlinked/superlinked/compare/v19.17.1..v19.18.0
[19.17.1]: https://github.com/superlinked/superlinked/compare/v19.17.0..v19.17.1
[19.16.0]: https://github.com/superlinked/superlinked/compare/v19.15.1..v19.16.0
[19.15.1]: https://github.com/superlinked/superlinked/compare/v19.15.0..v19.15.1
[19.15.0]: https://github.com/superlinked/superlinked/compare/v19.14.3..v19.15.0
[19.14.2]: https://github.com/superlinked/superlinked/compare/v19.14.1..v19.14.2
[19.14.1]: https://github.com/superlinked/superlinked/compare/v19.14.0..v19.14.1
[19.14.0]: https://github.com/superlinked/superlinked/compare/v19.13.0..v19.14.0
[19.13.0]: https://github.com/superlinked/superlinked/compare/v19.12.0..v19.13.0
[19.12.0]: https://github.com/superlinked/superlinked/compare/v19.11.0..v19.12.0
[19.11.0]: https://github.com/superlinked/superlinked/compare/v19.10.0..v19.11.0
[19.10.0]: https://github.com/superlinked/superlinked/compare/v19.9.0..v19.10.0
[19.9.0]: https://github.com/superlinked/superlinked/compare/v19.8.0..v19.9.0
[19.8.0]: https://github.com/superlinked/superlinked/compare/v19.7.3..v19.8.0
[19.7.3]: https://github.com/superlinked/superlinked/compare/v19.7.2..v19.7.3
[19.7.2]: https://github.com/superlinked/superlinked/compare/v19.7.1..v19.7.2
[19.7.1]: https://github.com/superlinked/superlinked/compare/v19.7.0..v19.7.1
[19.7.0]: https://github.com/superlinked/superlinked/compare/v19.6.0..v19.7.0
[19.5.0]: https://github.com/superlinked/superlinked/compare/v19.4.1..v19.5.0
[19.4.1]: https://github.com/superlinked/superlinked/compare/v19.4.0..v19.4.1
[19.4.0]: https://github.com/superlinked/superlinked/compare/v19.3.0..v19.4.0
[19.3.0]: https://github.com/superlinked/superlinked/compare/v19.2.3..v19.3.0
[19.2.2]: https://github.com/superlinked/superlinked/compare/v19.2.1..v19.2.2
[19.2.1]: https://github.com/superlinked/superlinked/compare/v19.2.0..v19.2.1
[19.2.0]: https://github.com/superlinked/superlinked/compare/v19.1.0..v19.2.0
[19.1.0]: https://github.com/superlinked/superlinked/compare/v19.0.1..v19.1.0
[19.0.0]: https://github.com/superlinked/superlinked/compare/v18.9.0..v19.0.0
[18.9.0]: https://github.com/superlinked/superlinked/compare/v18.8.0..v18.9.0
[18.8.0]: https://github.com/superlinked/superlinked/compare/v18.7.1..v18.8.0
[18.7.1]: https://github.com/superlinked/superlinked/compare/v18.7.0..v18.7.1
[18.7.0]: https://github.com/superlinked/superlinked/compare/v18.6.0..v18.7.0
[18.6.0]: https://github.com/superlinked/superlinked/compare/v18.5.0..v18.6.0
[18.5.0]: https://github.com/superlinked/superlinked/compare/v18.4.0..v18.5.0
[18.4.0]: https://github.com/superlinked/superlinked/compare/v18.3.0..v18.4.0
[18.3.0]: https://github.com/superlinked/superlinked/compare/v18.2.0..v18.3.0
[18.2.0]: https://github.com/superlinked/superlinked/compare/v18.1.1..v18.2.0
[18.1.1]: https://github.com/superlinked/superlinked/compare/v18.1.0..v18.1.1
[18.1.0]: https://github.com/superlinked/superlinked/compare/v18.0.1..v18.1.0
[18.0.1]: https://github.com/superlinked/superlinked/compare/v18.0.0..v18.0.1
[18.0.0]: https://github.com/superlinked/superlinked/compare/v17.9.2..v18.0.0
[17.9.2]: https://github.com/superlinked/superlinked/compare/v17.9.1..v17.9.2
[17.9.1]: https://github.com/superlinked/superlinked/compare/v17.9.0..v17.9.1
[17.9.0]: https://github.com/superlinked/superlinked/compare/v17.8.3..v17.9.0
[17.8.3]: https://github.com/superlinked/superlinked/compare/v17.8.2..v17.8.3
[17.8.2]: https://github.com/superlinked/superlinked/compare/v17.8.1..v17.8.2
[17.8.1]: https://github.com/superlinked/superlinked/compare/v17.8.0..v17.8.1
[17.8.0]: https://github.com/superlinked/superlinked/compare/v17.7.1..v17.8.0
[17.7.0]: https://github.com/superlinked/superlinked/compare/v17.6.0..v17.7.0
[17.6.0]: https://github.com/superlinked/superlinked/compare/v17.5.0..v17.6.0
[17.5.0]: https://github.com/superlinked/superlinked/compare/v17.4.0..v17.5.0
[17.4.0]: https://github.com/superlinked/superlinked/compare/v17.3.0..v17.4.0
[17.3.0]: https://github.com/superlinked/superlinked/compare/v17.2.2..v17.3.0
[17.2.2]: https://github.com/superlinked/superlinked/compare/v17.2.1..v17.2.2
[17.2.1]: https://github.com/superlinked/superlinked/compare/v17.2.0..v17.2.1
[17.2.0]: https://github.com/superlinked/superlinked/compare/v17.1.0..v17.2.0
[17.1.0]: https://github.com/superlinked/superlinked/compare/v17.0.1..v17.1.0
[17.0.1]: https://github.com/superlinked/superlinked/compare/v17.0.0..v17.0.1
[17.0.0]: https://github.com/superlinked/superlinked/compare/v16.3.0..v17.0.0
[16.3.0]: https://github.com/superlinked/superlinked/compare/v16.2.0..v16.3.0
[16.2.0]: https://github.com/superlinked/superlinked/compare/v16.1.9..v16.2.0
[16.1.8]: https://github.com/superlinked/superlinked/compare/v16.1.7..v16.1.8
[16.1.6]: https://github.com/superlinked/superlinked/compare/v16.1.5..v16.1.6
[16.1.5]: https://github.com/superlinked/superlinked/compare/v16.1.4..v16.1.5
[16.1.4]: https://github.com/superlinked/superlinked/compare/v16.1.3..v16.1.4
[16.1.2]: https://github.com/superlinked/superlinked/compare/v16.1.1..v16.1.2
[16.1.1]: https://github.com/superlinked/superlinked/compare/v16.1.0..v16.1.1
[16.1.0]: https://github.com/superlinked/superlinked/compare/v16.0.0..v16.1.0
[16.0.0]: https://github.com/superlinked/superlinked/compare/v15.2.0..v16.0.0
[15.2.0]: https://github.com/superlinked/superlinked/compare/v15.1.1..v15.2.0
[15.1.1]: https://github.com/superlinked/superlinked/compare/v15.1.0..v15.1.1
[15.0.0]: https://github.com/superlinked/superlinked/compare/v14.7.1..v15.0.0
[14.7.1]: https://github.com/superlinked/superlinked/compare/v14.7.0..v14.7.1
[14.7.0]: https://github.com/superlinked/superlinked/compare/v14.6.1..v14.7.0
[14.6.1]: https://github.com/superlinked/superlinked/compare/v14.6.0..v14.6.1
[14.6.0]: https://github.com/superlinked/superlinked/compare/v14.5.0..v14.6.0
[14.5.0]: https://github.com/superlinked/superlinked/compare/v14.4.1..v14.5.0
[14.4.1]: https://github.com/superlinked/superlinked/compare/v14.4.0..v14.4.1
[14.4.0]: https://github.com/superlinked/superlinked/compare/v14.3.0..v14.4.0
[14.3.0]: https://github.com/superlinked/superlinked/compare/v14.2.0..v14.3.0
[14.1.1]: https://github.com/superlinked/superlinked/compare/v14.1.0..v14.1.1
[14.1.0]: https://github.com/superlinked/superlinked/compare/v14.0.0..v14.1.0
[13.1.3]: https://github.com/superlinked/superlinked/compare/v13.1.2..v13.1.3
[13.1.2]: https://github.com/superlinked/superlinked/compare/v13.1.1..v13.1.2
[13.1.1]: https://github.com/superlinked/superlinked/compare/v13.1.0..v13.1.1
[12.28.1]: https://github.com/superlinked/superlinked/compare/v12.28.0..v12.28.1
[12.28.0]: https://github.com/superlinked/superlinked/compare/v12.27.0..v12.28.0
[12.27.0]: https://github.com/superlinked/superlinked/compare/v12.26.0..v12.27.0
[12.25.0]: https://github.com/superlinked/superlinked/compare/v12.24.2..v12.25.0
[12.24.2]: https://github.com/superlinked/superlinked/compare/v12.24.1..v12.24.2
[12.24.1]: https://github.com/superlinked/superlinked/compare/v12.24.0..v12.24.1
[12.23.0]: https://github.com/superlinked/superlinked/compare/v12.22.3..v12.23.0
[12.22.0]: https://github.com/superlinked/superlinked/compare/v12.21.0..v12.22.0
[12.21.0]: https://github.com/superlinked/superlinked/compare/v12.20.1..v12.21.0
[12.20.1]: https://github.com/superlinked/superlinked/compare/v12.20.0..v12.20.1
[12.20.0]: https://github.com/superlinked/superlinked/compare/v12.19.1..v12.20.0
[12.19.0]: https://github.com/superlinked/superlinked/compare/v12.18.4..v12.19.0
[12.18.3]: https://github.com/superlinked/superlinked/compare/v12.18.2..v12.18.3
[12.18.1]: https://github.com/superlinked/superlinked/compare/v12.18.0..v12.18.1
[12.18.0]: https://github.com/superlinked/superlinked/compare/v12.17.1..v12.18.0
[12.17.0]: https://github.com/superlinked/superlinked/compare/v12.16.0..v12.17.0
[12.16.0]: https://github.com/superlinked/superlinked/compare/v12.15.0..v12.16.0
[12.14.0]: https://github.com/superlinked/superlinked/compare/v12.13.1..v12.14.0
[12.13.1]: https://github.com/superlinked/superlinked/compare/v12.13.0..v12.13.1
[12.13.0]: https://github.com/superlinked/superlinked/compare/v12.12.0..v12.13.0
[12.10.0]: https://github.com/superlinked/superlinked/compare/v12.9.0..v12.10.0
[12.9.0]: https://github.com/superlinked/superlinked/compare/v12.8.0..v12.9.0
[12.8.0]: https://github.com/superlinked/superlinked/compare/v12.7.3..v12.8.0
[12.7.3]: https://github.com/superlinked/superlinked/compare/v12.7.2..v12.7.3
[12.7.2]: https://github.com/superlinked/superlinked/compare/v12.7.1..v12.7.2
[12.7.1]: https://github.com/superlinked/superlinked/compare/v12.7.0..v12.7.1
[12.6.0]: https://github.com/superlinked/superlinked/compare/v12.5.0..v12.6.0
[12.4.0]: https://github.com/superlinked/superlinked/compare/v12.3.0..v12.4.0
[12.3.0]: https://github.com/superlinked/superlinked/compare/v12.2.0..v12.3.0
[12.2.0]: https://github.com/superlinked/superlinked/compare/v12.1.0..v12.2.0
[12.1.0]: https://github.com/superlinked/superlinked/compare/v12.0.0..v12.1.0
[11.1.0]: https://github.com/superlinked/superlinked/compare/v11.0.0..v11.1.0
[11.0.0]: https://github.com/superlinked/superlinked/compare/v10.2.2..v11.0.0
[10.2.2]: https://github.com/superlinked/superlinked/compare/v10.2.1..v10.2.2
[10.2.0]: https://github.com/superlinked/superlinked/compare/v10.1.1..v10.2.0
[10.1.1]: https://github.com/superlinked/superlinked/compare/v10.1.0..v10.1.1
[10.1.0]: https://github.com/superlinked/superlinked/compare/v10.0.0..v10.1.0
[10.0.0]: https://github.com/superlinked/superlinked/compare/v9.49.0..v10.0.0
[9.48.6]: https://github.com/superlinked/superlinked/compare/v9.48.5..v9.48.6
[9.48.4]: https://github.com/superlinked/superlinked/compare/v9.48.3..v9.48.4
[9.48.2]: https://github.com/superlinked/superlinked/compare/v9.48.1..v9.48.2
[9.48.1]: https://github.com/superlinked/superlinked/compare/v9.48.0..v9.48.1
[9.48.0]: https://github.com/superlinked/superlinked/compare/v9.47.1..v9.48.0
[9.47.1]: https://github.com/superlinked/superlinked/compare/v9.47.0..v9.47.1
[9.47.0]: https://github.com/superlinked/superlinked/compare/v9.46.3..v9.47.0
[9.46.3]: https://github.com/superlinked/superlinked/compare/v9.46.2..v9.46.3
[9.46.1]: https://github.com/superlinked/superlinked/compare/v9.46.0..v9.46.1
[9.46.0]: https://github.com/superlinked/superlinked/compare/v9.45.0..v9.46.0
[9.45.0]: https://github.com/superlinked/superlinked/compare/v9.44.1..v9.45.0
[9.44.0]: https://github.com/superlinked/superlinked/compare/v9.43.1..v9.44.0
[9.43.1]: https://github.com/superlinked/superlinked/compare/v9.43.0..v9.43.1
[9.43.0]: https://github.com/superlinked/superlinked/compare/v9.42.1..v9.43.0
[9.42.1]: https://github.com/superlinked/superlinked/compare/v9.42.0..v9.42.1
[9.42.0]: https://github.com/superlinked/superlinked/compare/v9.41.1..v9.42.0
[9.41.1]: https://github.com/superlinked/superlinked/compare/v9.41.0..v9.41.1
[9.40.0]: https://github.com/superlinked/superlinked/compare/v9.39.0..v9.40.0
[9.38.1]: https://github.com/superlinked/superlinked/compare/v9.38.0..v9.38.1
[9.38.0]: https://github.com/superlinked/superlinked/compare/v9.37.1..v9.38.0
[9.37.0]: https://github.com/superlinked/superlinked/compare/v9.36.0..v9.37.0
[9.36.0]: https://github.com/superlinked/superlinked/compare/v9.35.1..v9.36.0
[9.35.1]: https://github.com/superlinked/superlinked/compare/v9.35.0..v9.35.1
[9.34.0]: https://github.com/superlinked/superlinked/compare/v9.33.0..v9.34.0
[9.33.0]: https://github.com/superlinked/superlinked/compare/v9.32.2..v9.33.0
[9.32.1]: https://github.com/superlinked/superlinked/compare/v9.32.0..v9.32.1
[9.32.0]: https://github.com/superlinked/superlinked/compare/v9.31.0..v9.32.0
[9.31.0]: https://github.com/superlinked/superlinked/compare/v9.30.0..v9.31.0
[9.30.0]: https://github.com/superlinked/superlinked/compare/v9.29.1..v9.30.0
[9.29.0]: https://github.com/superlinked/superlinked/compare/v9.28.0..v9.29.0
[9.27.2]: https://github.com/superlinked/superlinked/compare/v9.27.1..v9.27.2
[9.27.1]: https://github.com/superlinked/superlinked/compare/v9.27.0..v9.27.1
[9.27.0]: https://github.com/superlinked/superlinked/compare/v9.26.0..v9.27.0
[9.26.0]: https://github.com/superlinked/superlinked/compare/v9.25.1..v9.26.0
[9.25.1]: https://github.com/superlinked/superlinked/compare/v9.25.0..v9.25.1
[9.24.0]: https://github.com/superlinked/superlinked/compare/v9.23.2..v9.24.0
[9.23.2]: https://github.com/superlinked/superlinked/compare/v9.23.1..v9.23.2
[9.23.1]: https://github.com/superlinked/superlinked/compare/v9.23.0..v9.23.1
[9.23.0]: https://github.com/superlinked/superlinked/compare/v9.22.1..v9.23.0
[9.22.0]: https://github.com/superlinked/superlinked/compare/v9.21.2..v9.22.0
[9.21.1]: https://github.com/superlinked/superlinked/compare/v9.21.0..v9.21.1
[9.19.1]: https://github.com/superlinked/superlinked/compare/v9.19.0..v9.19.1
[9.19.0]: https://github.com/superlinked/superlinked/compare/v9.18.0..v9.19.0
[9.18.0]: https://github.com/superlinked/superlinked/compare/v9.17.2..v9.18.0
[9.17.0]: https://github.com/superlinked/superlinked/compare/v9.16.3..v9.17.0
[9.16.3]: https://github.com/superlinked/superlinked/compare/v9.16.2..v9.16.3
[9.16.2]: https://github.com/superlinked/superlinked/compare/v9.16.1..v9.16.2
[9.15.0]: https://github.com/superlinked/superlinked/compare/v9.14.0..v9.15.0
[9.13.0]: https://github.com/superlinked/superlinked/compare/v9.12.1..v9.13.0
[9.12.1]: https://github.com/superlinked/superlinked/compare/v9.12.0..v9.12.1
[9.12.0]: https://github.com/superlinked/superlinked/compare/v9.11.0..v9.12.0
[9.9.0]: https://github.com/superlinked/superlinked/compare/v9.8.0..v9.9.0
[9.8.0]: https://github.com/superlinked/superlinked/compare/v9.7.2..v9.8.0
[9.7.2]: https://github.com/superlinked/superlinked/compare/v9.7.1..v9.7.2
[9.7.1]: https://github.com/superlinked/superlinked/compare/v9.7.0..v9.7.1
[9.7.0]: https://github.com/superlinked/superlinked/compare/v9.6.0..v9.7.0
[9.6.0]: https://github.com/superlinked/superlinked/compare/v9.5.0..v9.6.0
[9.4.0]: https://github.com/superlinked/superlinked/compare/v9.3.1..v9.4.0
[9.3.1]: https://github.com/superlinked/superlinked/compare/v9.3.0..v9.3.1
[9.3.0]: https://github.com/superlinked/superlinked/compare/v9.2.0..v9.3.0
[9.2.0]: https://github.com/superlinked/superlinked/compare/v9.1.1..v9.2.0
[9.1.1]: https://github.com/superlinked/superlinked/compare/v9.1.0..v9.1.1
[9.1.0]: https://github.com/superlinked/superlinked/compare/v9.0.0..v9.1.0
[8.13.0]: https://github.com/superlinked/superlinked/compare/v8.12.2..v8.13.0
[8.12.1]: https://github.com/superlinked/superlinked/compare/v8.12.0..v8.12.1
[8.12.0]: https://github.com/superlinked/superlinked/compare/v8.11.0..v8.12.0
[8.11.0]: https://github.com/superlinked/superlinked/compare/v8.10.0..v8.11.0
[8.10.0]: https://github.com/superlinked/superlinked/compare/v8.9.0..v8.10.0
[8.9.0]: https://github.com/superlinked/superlinked/compare/v8.8.3..v8.9.0
[8.8.2]: https://github.com/superlinked/superlinked/compare/v8.8.1..v8.8.2
[8.8.0]: https://github.com/superlinked/superlinked/compare/v8.7.4..v8.8.0
[8.7.4]: https://github.com/superlinked/superlinked/compare/v8.7.3..v8.7.4
[8.7.3]: https://github.com/superlinked/superlinked/compare/v8.7.2..v8.7.3
[8.7.2]: https://github.com/superlinked/superlinked/compare/v8.7.1..v8.7.2
[8.7.1]: https://github.com/superlinked/superlinked/compare/v8.7.0..v8.7.1
[8.6.8]: https://github.com/superlinked/superlinked/compare/v8.6.7..v8.6.8
[8.6.7]: https://github.com/superlinked/superlinked/compare/v8.6.6..v8.6.7
[8.6.5]: https://github.com/superlinked/superlinked/compare/v8.6.4..v8.6.5
[8.6.4]: https://github.com/superlinked/superlinked/compare/v8.6.3..v8.6.4
[8.5.2]: https://github.com/superlinked/superlinked/compare/v8.5.1..v8.5.2
[8.5.1]: https://github.com/superlinked/superlinked/compare/v8.5.0..v8.5.1
[8.5.0]: https://github.com/superlinked/superlinked/compare/v8.4.1..v8.5.0
[8.4.1]: https://github.com/superlinked/superlinked/compare/v8.4.0..v8.4.1
[8.2.0]: https://github.com/superlinked/superlinked/compare/v8.1.0..v8.2.0
[8.1.0]: https://github.com/superlinked/superlinked/compare/v8.0.1..v8.1.0
[8.0.0]: https://github.com/superlinked/superlinked/compare/v7.5.0..v8.0.0
[7.5.0]: https://github.com/superlinked/superlinked/compare/v7.4.0..v7.5.0
[7.4.0]: https://github.com/superlinked/superlinked/compare/v7.3.0..v7.4.0
[7.3.0]: https://github.com/superlinked/superlinked/compare/v7.2.1..v7.3.0
[7.2.0]: https://github.com/superlinked/superlinked/compare/v7.1.0..v7.2.0
[7.1.0]: https://github.com/superlinked/superlinked/compare/v7.0.6..v7.1.0
[7.0.6]: https://github.com/superlinked/superlinked/compare/v7.0.5..v7.0.6
[7.0.5]: https://github.com/superlinked/superlinked/compare/v7.0.4..v7.0.5
[7.0.1]: https://github.com/superlinked/superlinked/compare/v7.0.0..v7.0.1
[7.0.0]: https://github.com/superlinked/superlinked/compare/v6.10.0..v7.0.0
[6.10.0]: https://github.com/superlinked/superlinked/compare/v6.9.0..v6.10.0
[6.9.0]: https://github.com/superlinked/superlinked/compare/v6.8.0..v6.9.0
[6.8.0]: https://github.com/superlinked/superlinked/compare/v6.7.1..v6.8.0
[6.7.1]: https://github.com/superlinked/superlinked/compare/v6.7.0..v6.7.1
[6.5.6]: https://github.com/superlinked/superlinked/compare/v6.5.5..v6.5.6
[6.5.5]: https://github.com/superlinked/superlinked/compare/v6.5.4..v6.5.5
[6.5.3]: https://github.com/superlinked/superlinked/compare/v6.5.2..v6.5.3
[6.5.2]: https://github.com/superlinked/superlinked/compare/v6.5.1..v6.5.2
[6.5.1]: https://github.com/superlinked/superlinked/compare/v6.5.0..v6.5.1
[6.5.0]: https://github.com/superlinked/superlinked/compare/v6.4.0..v6.5.0
[6.4.0]: https://github.com/superlinked/superlinked/compare/v6.3.0..v6.4.0
[6.3.0]: https://github.com/superlinked/superlinked/compare/v6.2.0..v6.3.0
[6.2.0]: https://github.com/superlinked/superlinked/compare/v6.1.0..v6.2.0
[6.1.0]: https://github.com/superlinked/superlinked/compare/v6.0.1..v6.1.0
[6.0.1]: https://github.com/superlinked/superlinked/compare/v6.0.0..v6.0.1
[6.0.0]: https://github.com/superlinked/superlinked/compare/v5.11.0..v6.0.0
[5.11.0]: https://github.com/superlinked/superlinked/compare/v5.10.0..v5.11.0
[5.10.0]: https://github.com/superlinked/superlinked/compare/v5.9.0..v5.10.0
[5.8.1]: https://github.com/superlinked/superlinked/compare/v5.8.0..v5.8.1
[5.8.0]: https://github.com/superlinked/superlinked/compare/v5.7.0..v5.8.0
[5.5.2]: https://github.com/superlinked/superlinked/compare/v5.5.1..v5.5.2
[5.5.1]: https://github.com/superlinked/superlinked/compare/v5.5.0..v5.5.1
[5.4.1]: https://github.com/superlinked/superlinked/compare/v5.4.0..v5.4.1
[5.4.0]: https://github.com/superlinked/superlinked/compare/v5.3.0..v5.4.0
[5.3.0]: https://github.com/superlinked/superlinked/compare/v5.2.3..v5.3.0
[5.2.3]: https://github.com/superlinked/superlinked/compare/v5.2.2..v5.2.3
[5.2.2]: https://github.com/superlinked/superlinked/compare/v5.2.1..v5.2.2
[5.2.1]: https://github.com/superlinked/superlinked/compare/v5.2.0..v5.2.1
[5.2.0]: https://github.com/superlinked/superlinked/compare/v5.1.0..v5.2.0
[5.0.0]: https://github.com/superlinked/superlinked/compare/v4.1.0..v5.0.0
[4.1.0]: https://github.com/superlinked/superlinked/compare/v4.0.1..v4.1.0
[4.0.1]: https://github.com/superlinked/superlinked/compare/v4.0.0..v4.0.1
[3.46.0]: https://github.com/superlinked/superlinked/compare/v3.45.0..v3.46.0
[3.45.0]: https://github.com/superlinked/superlinked/compare/v3.44.0..v3.45.0
[3.44.0]: https://github.com/superlinked/superlinked/compare/v3.43.0..v3.44.0
[3.42.0]: https://github.com/superlinked/superlinked/compare/v3.41.1..v3.42.0
[3.41.1]: https://github.com/superlinked/superlinked/compare/v3.41.0..v3.41.1
[3.41.0]: https://github.com/superlinked/superlinked/compare/v3.40.0..v3.41.0
[3.40.0]: https://github.com/superlinked/superlinked/compare/v3.39.1..v3.40.0
[3.39.1]: https://github.com/superlinked/superlinked/compare/v3.39.0..v3.39.1
[3.39.0]: https://github.com/superlinked/superlinked/compare/v3.38.0..v3.39.0
[3.38.0]: https://github.com/superlinked/superlinked/compare/v3.37.2..v3.38.0
[3.37.2]: https://github.com/superlinked/superlinked/compare/v3.37.1..v3.37.2
[3.37.1]: https://github.com/superlinked/superlinked/compare/v3.37.0..v3.37.1
[3.36.0]: https://github.com/superlinked/superlinked/compare/v3.35.2..v3.36.0
[3.35.2]: https://github.com/superlinked/superlinked/compare/v3.35.1..v3.35.2
[3.35.1]: https://github.com/superlinked/superlinked/compare/v3.35.0..v3.35.1
[3.35.0]: https://github.com/superlinked/superlinked/compare/v3.34.1..v3.35.0
[3.34.1]: https://github.com/superlinked/superlinked/compare/v3.34.0..v3.34.1
[3.34.0]: https://github.com/superlinked/superlinked/compare/v3.33.0..v3.34.0
[3.33.0]: https://github.com/superlinked/superlinked/compare/v3.32.0..v3.33.0
[3.32.0]: https://github.com/superlinked/superlinked/compare/v3.31.0..v3.32.0
[3.31.0]: https://github.com/superlinked/superlinked/compare/v3.30.0..v3.31.0
[3.29.2]: https://github.com/superlinked/superlinked/compare/v3.29.1..v3.29.2
[3.29.1]: https://github.com/superlinked/superlinked/compare/v3.29.0..v3.29.1
[3.28.0]: https://github.com/superlinked/superlinked/compare/v3.27.0..v3.28.0
[3.27.0]: https://github.com/superlinked/superlinked/compare/v3.26.0..v3.27.0
[3.26.0]: https://github.com/superlinked/superlinked/compare/v3.25.0..v3.26.0
[3.23.0]: https://github.com/superlinked/superlinked/compare/v3.22.0..v3.23.0
[3.22.0]: https://github.com/superlinked/superlinked/compare/v3.21.0..v3.22.0
[3.21.0]: https://github.com/superlinked/superlinked/compare/v3.20.0..v3.21.0
[3.20.0]: https://github.com/superlinked/superlinked/compare/v3.19.0..v3.20.0
[3.18.1]: https://github.com/superlinked/superlinked/compare/v3.18.0..v3.18.1
[3.18.0]: https://github.com/superlinked/superlinked/compare/v3.17.0..v3.18.0
[3.17.0]: https://github.com/superlinked/superlinked/compare/v3.16.0..v3.17.0
[3.16.0]: https://github.com/superlinked/superlinked/compare/v3.15.1..v3.16.0
[3.15.1]: https://github.com/superlinked/superlinked/compare/v3.15.0..v3.15.1
[3.15.0]: https://github.com/superlinked/superlinked/compare/v3.14.4..v3.15.0
[3.14.4]: https://github.com/superlinked/superlinked/compare/v3.14.3..v3.14.4
[3.14.3]: https://github.com/superlinked/superlinked/compare/v3.14.2..v3.14.3
[3.14.1]: https://github.com/superlinked/superlinked/compare/v3.14.0..v3.14.1
[3.14.0]: https://github.com/superlinked/superlinked/compare/v3.13.0..v3.14.0
[3.12.0]: https://github.com/superlinked/superlinked/compare/v3.11.0..v3.12.0
[3.11.0]: https://github.com/superlinked/superlinked/compare/v3.10.0..v3.11.0
[3.8.0]: https://github.com/superlinked/superlinked/compare/v3.7.0..v3.8.0
[3.7.0]: https://github.com/superlinked/superlinked/compare/v3.6.3..v3.7.0
[3.6.0]: https://github.com/superlinked/superlinked/compare/v3.5.0..v3.6.0
[3.5.0]: https://github.com/superlinked/superlinked/compare/v3.4.1..v3.5.0
[3.4.0]: https://github.com/superlinked/superlinked/compare/v3.3.0..v3.4.0
[3.3.0]: https://github.com/superlinked/superlinked/compare/v3.2.1..v3.3.0
[3.2.1]: https://github.com/superlinked/superlinked/compare/v3.2.0..v3.2.1
[3.2.0]: https://github.com/superlinked/superlinked/compare/v3.1.0..v3.2.0
[3.1.0]: https://github.com/superlinked/superlinked/compare/v3.0.0..v3.1.0
[3.0.0]: https://github.com/superlinked/superlinked/compare/v2.37.0..v3.0.0
[2.37.0]: https://github.com/superlinked/superlinked/compare/v2.36.0..v2.37.0
[2.35.0]: https://github.com/superlinked/superlinked/compare/v2.34.0..v2.35.0
[2.33.2]: https://github.com/superlinked/superlinked/compare/v2.33.1..v2.33.2
[2.33.0]: https://github.com/superlinked/superlinked/compare/v2.32.6..v2.33.0
[2.32.5]: https://github.com/superlinked/superlinked/compare/v2.32.4..v2.32.5
[2.32.1]: https://github.com/superlinked/superlinked/compare/v2.32.0..v2.32.1
[2.32.0]: https://github.com/superlinked/superlinked/compare/v2.31.0..v2.32.0
[2.31.0]: https://github.com/superlinked/superlinked/compare/v2.30.0..v2.31.0
[2.30.0]: https://github.com/superlinked/superlinked/compare/v2.29.0..v2.30.0
[2.29.0]: https://github.com/superlinked/superlinked/compare/v2.28.0..v2.29.0
[2.28.0]: https://github.com/superlinked/superlinked/compare/v2.27.1..v2.28.0
[2.27.0]: https://github.com/superlinked/superlinked/compare/v2.26.1..v2.27.0
[2.26.0]: https://github.com/superlinked/superlinked/compare/v2.25.0..v2.26.0
[2.25.0]: https://github.com/superlinked/superlinked/compare/v2.24.0..v2.25.0
[2.24.0]: https://github.com/superlinked/superlinked/compare/v2.23.3..v2.24.0
[2.23.3]: https://github.com/superlinked/superlinked/compare/v2.23.2..v2.23.3
[2.23.2]: https://github.com/superlinked/superlinked/compare/v2.23.1..v2.23.2
[2.23.1]: https://github.com/superlinked/superlinked/compare/v2.23.0..v2.23.1
[2.23.0]: https://github.com/superlinked/superlinked/compare/v2.22.0..v2.23.0
[2.22.0]: https://github.com/superlinked/superlinked/compare/v2.21.0..v2.22.0
[2.21.0]: https://github.com/superlinked/superlinked/compare/v2.20.0..v2.21.0
[2.20.0]: https://github.com/superlinked/superlinked/compare/v2.19.0..v2.20.0
[2.19.0]: https://github.com/superlinked/superlinked/compare/v2.18.0..v2.19.0
[2.17.4]: https://github.com/superlinked/superlinked/compare/v2.17.3..v2.17.4
[2.17.2]: https://github.com/superlinked/superlinked/compare/v2.17.1..v2.17.2
[2.17.1]: https://github.com/superlinked/superlinked/compare/v2.17.0..v2.17.1
[2.17.0]: https://github.com/superlinked/superlinked/compare/v2.16.0..v2.17.0
[2.16.0]: https://github.com/superlinked/superlinked/compare/v2.15.0..v2.16.0
[2.14.2]: https://github.com/superlinked/superlinked/compare/v2.14.1..v2.14.2
[2.14.1]: https://github.com/superlinked/superlinked/compare/v2.14.0..v2.14.1
[2.14.0]: https://github.com/superlinked/superlinked/compare/v2.13.0..v2.14.0
[2.12.0]: https://github.com/superlinked/superlinked/compare/v2.11.0..v2.12.0
[2.11.0]: https://github.com/superlinked/superlinked/compare/v2.10.0..v2.11.0
[2.10.0]: https://github.com/superlinked/superlinked/compare/v2.9.0..v2.10.0
[2.9.0]: https://github.com/superlinked/superlinked/compare/v2.8.0..v2.9.0
[2.8.0]: https://github.com/superlinked/superlinked/compare/v2.7.2..v2.8.0
[2.7.1]: https://github.com/superlinked/superlinked/compare/v2.7.0..v2.7.1
[2.6.0]: https://github.com/superlinked/superlinked/compare/v2.5.0..v2.6.0
[2.5.0]: https://github.com/superlinked/superlinked/compare/v2.4.1..v2.5.0
[2.4.1]: https://github.com/superlinked/superlinked/compare/v2.4.0..v2.4.1
[2.4.0]: https://github.com/superlinked/superlinked/compare/v2.3.0..v2.4.0
[2.3.0]: https://github.com/superlinked/superlinked/compare/v2.2.0..v2.3.0
[2.2.0]: https://github.com/superlinked/superlinked/compare/v2.1.4..v2.2.0
[2.1.4]: https://github.com/superlinked/superlinked/compare/v2.1.3..v2.1.4
[2.1.3]: https://github.com/superlinked/superlinked/compare/v2.1.2..v2.1.3
[2.1.2]: https://github.com/superlinked/superlinked/compare/v2.1.1..v2.1.2
[2.1.1]: https://github.com/superlinked/superlinked/compare/v2.1.0..v2.1.1
[2.1.0]: https://github.com/superlinked/superlinked/compare/v2.0.0..v2.1.0
[2.0.0]: https://github.com/superlinked/superlinked/compare/v1.11.3..v2.0.0
[1.11.3]: https://github.com/superlinked/superlinked/compare/v1.11.2..v1.11.3
[1.11.2]: https://github.com/superlinked/superlinked/compare/v1.11.1..v1.11.2
[1.11.1]: https://github.com/superlinked/superlinked/compare/v1.11.0..v1.11.1
[1.11.0]: https://github.com/superlinked/superlinked/compare/v1.10.1..v1.11.0
[1.10.1]: https://github.com/superlinked/superlinked/compare/v1.10.0..v1.10.1
[1.10.0]: https://github.com/superlinked/superlinked/compare/v1.9.0..v1.10.0
[1.9.0]: https://github.com/superlinked/superlinked/compare/v1.8.1..v1.9.0
[1.8.1]: https://github.com/superlinked/superlinked/compare/v1.8.0..v1.8.1
[1.8.0]: https://github.com/superlinked/superlinked/compare/v1.7.1..v1.8.0
[1.7.0]: https://github.com/superlinked/superlinked/compare/v1.6.0..v1.7.0
[1.6.0]: https://github.com/superlinked/superlinked/compare/v1.5.0..v1.6.0
[1.5.0]: https://github.com/superlinked/superlinked/compare/v1.4.0..v1.5.0
[1.4.0]: https://github.com/superlinked/superlinked/compare/v1.3.0..v1.4.0
[1.3.0]: https://github.com/superlinked/superlinked/compare/v1.2.0..v1.3.0
[1.2.0]: https://github.com/superlinked/superlinked/compare/v1.1.0..v1.2.0
[1.1.0]: https://github.com/superlinked/superlinked/compare/v1.0.0..v1.1.0
[1.0.0]: https://github.com/superlinked/superlinked/compare/v0.9.0..v1.0.0
[0.9.0]: https://github.com/superlinked/superlinked/compare/v0.8.0..v0.9.0
[0.8.0]: https://github.com/superlinked/superlinked/compare/v0.7.0..v0.8.0
[0.7.0]: https://github.com/superlinked/superlinked/compare/v0.6.0..v0.7.0
[0.6.0]: https://github.com/superlinked/superlinked/compare/v0.5.1..v0.6.0
[0.5.1]: https://github.com/superlinked/superlinked/compare/v0.5.0..v0.5.1
[0.5.0]: https://github.com/superlinked/superlinked/compare/v0.4.1..v0.5.0
[0.4.1]: https://github.com/superlinked/superlinked/compare/v0.4.0..v0.4.1
[0.4.0]: https://github.com/superlinked/superlinked/compare/v0.3.0..v0.4.0
[0.3.0]: https://github.com/superlinked/superlinked/compare/v0.2.3..v0.3.0
[0.2.3]: https://github.com/superlinked/superlinked/compare/v0.2.2..v0.2.3
[0.2.2]: https://github.com/superlinked/superlinked/compare/v0.2.1..v0.2.2
[0.2.1]: https://github.com/superlinked/superlinked/compare/v0.2.0..v0.2.1
[0.2.0]: https://github.com/superlinked/superlinked/compare/v0.1.3..v0.2.0
[0.1.3]: https://github.com/superlinked/superlinked/compare/v0.1.1..v0.1.3
[0.1.1]: https://github.com/superlinked/superlinked/compare/v0.1.0..v0.1.1
[0.1.0]: https://github.com/superlinked/superlinked/compare/v0.0.12..v0.1.0
[0.0.12]: https://github.com/superlinked/superlinked/compare/v0.0.11..v0.0.12
[0.0.10]: https://github.com/superlinked/superlinked/compare/v0.0.9..v0.0.10
[0.0.9]: https://github.com/superlinked/superlinked/compare/v0.0.8..v0.0.9
[0.0.8]: https://github.com/superlinked/superlinked/compare/v0.0.7..v0.0.8
[0.0.7]: https://github.com/superlinked/superlinked/compare/v0.0.6..v0.0.7
[0.0.6]: https://github.com/superlinked/superlinked/compare/v0.0.5..v0.0.6
[0.0.5]: https://github.com/superlinked/superlinked/compare/v0.0.4..v0.0.5

