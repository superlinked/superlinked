# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


try:
    # altair dependency is optional
    from superlinked.evaluation.charts.recency_plotter import RecencyPlotter
except ImportError:
    pass

try:
    # pymongo dependency is optional
    from superlinked.framework.dsl.storage.mongo_db_vector_database import (
        MongoDBVectorDatabase,
    )
except ImportError:
    pass

try:
    # qdrant dependency is optional
    from superlinked.framework.dsl.storage.qdrant_vector_database import (
        QdrantVectorDatabase,
    )
except ImportError:
    pass

try:
    # redis dependency is optional
    from superlinked.framework.dsl.storage.redis_vector_database import (
        RedisVectorDatabase,
    )
except ImportError:
    pass
from superlinked.evaluation.pandas_converter import PandasConverter
from superlinked.evaluation.vector_sampler import VectorSampler
from superlinked.framework.blob.blob_handler_factory import BlobHandlerConfig
from superlinked.framework.common.dag.context import CONTEXT_COMMON, CONTEXT_COMMON_NOW
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.parser.dataframe_parser import DataFrameParser
from superlinked.framework.common.parser.json_parser import JsonParser
from superlinked.framework.common.schema.event_schema import EventSchema, event_schema
from superlinked.framework.common.schema.event_schema_object import (
    CreatedAtField,
    SchemaReference,
)
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.schema import Schema, schema
from superlinked.framework.common.schema.schema_object import (
    Blob,
    Boolean,
    DescribedBlob,
    Float,
    FloatList,
    Integer,
    String,
    StringList,
    Timestamp,
)
from superlinked.framework.common.space.config.embedding.image_embedding_config import (
    ModelHandler,
)
from superlinked.framework.common.space.config.embedding.number_embedding_config import (
    LinearScale,
    LogarithmicScale,
    Mode,
)
from superlinked.framework.common.space.config.embedding.text_similarity_embedding_config import (
    TextModelHandler,
)
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.util.interactive_util import get_altair_renderer
from superlinked.framework.dsl.app.interactive.interactive_app import InteractiveApp
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryApp,
    InMemoryExecutor,
)
from superlinked.framework.dsl.executor.interactive.interactive_executor import (
    InteractiveExecutor,
)
from superlinked.framework.dsl.executor.rest.rest_configuration import RestQuery
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.effect import Effect
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.query.result import QueryResult
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.data_loader_source import (
    DataFormat,
    DataLoaderConfig,
    DataLoaderSource,
)
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.source.interactive_source import InteractiveSource
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.custom_space import CustomSpace
from superlinked.framework.dsl.space.image_space import ImageSpace
from superlinked.framework.dsl.space.number_space import NumberSpace
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.text_similarity_space import (
    TextSimilaritySpace,
    chunk,
)
from superlinked.framework.dsl.storage.in_memory_vector_database import (
    InMemoryVectorDatabase,
)

__all__ = [
    # Evaluation
    "PandasConverter",
    "RecencyPlotter",
    "VectorSampler",
    # Framework Common recency
    "CONTEXT_COMMON",
    "CONTEXT_COMMON_NOW",
    "PeriodTime",
    # Framework Common nlq
    "OpenAIClientConfig",
    # Framework Common util
    "get_altair_renderer",
    # Framework Common parsers
    "DataFrameParser",
    "JsonParser",
    # Framework Common schema parents
    "EventSchema",
    "Schema",
    # Framework Common schema decorators
    "event_schema",
    "schema",
    # Framework Common Fields
    "Blob",
    "CreatedAtField",
    "Float",
    "FloatList",
    "IdField",
    "Integer",
    "Boolean",
    "SchemaReference",
    "String",
    "StringList",
    "Timestamp",
    "DescribedBlob",
    # Number Space Config
    "Mode",
    # Text Similarity Space Config
    "TextModelHandler",
    # DB
    "SearchAlgorithm",
    "InMemoryVectorDatabase",
    "MongoDBVectorDatabase",
    "QdrantVectorDatabase",
    "RedisVectorDatabase",
    # Data loader
    "DataFormat",
    "DataLoaderConfig",
    "DataLoaderSource",
    # DSL App
    "InteractiveApp",
    "InMemoryApp",
    # DSL Executor
    "InMemoryExecutor",
    "InteractiveExecutor",
    "RestExecutor",
    # DSL Source
    "InteractiveSource",
    "InMemorySource",
    "RestSource",
    # DSL Index
    "Effect",
    "Index",
    # DSL Query
    "Param",
    "Query",
    "RestQuery",
    "QueryResult",
    # DSL Space
    "Space",
    "CategoricalSimilaritySpace",
    "CustomSpace",
    "ImageSpace",
    "NumberSpace",
    "RecencySpace",
    "TextSimilaritySpace",
    # DSL Executor util
    "RestDescriptor",
    # DSL ImageSpace util
    "ModelHandler",
    # DSL TextSimilaritySpace util
    "chunk",
    # DSL NumberSpace util
    "LinearScale",
    "LogarithmicScale",
    # misc
    "SuperlinkedRegistry",
    "BlobHandlerConfig",
]

from superlinked.framework.common.superlinked_logging import (
    SuperlinkedLoggerConfigurator,
)

SuperlinkedLoggerConfigurator.configure_default_logger()
