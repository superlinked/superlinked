from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase

from .index import car_schema, index
from .query import query

car_source: RestSource = RestSource(car_schema)

executor = RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
