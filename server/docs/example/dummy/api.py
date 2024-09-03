from superlinked.framework.dsl.executor.rest.rest_configuration import RestQuery
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase

from .index import index, your_schema
from .query import query

your_source: RestSource = RestSource(your_schema)
your_query = RestQuery(RestDescriptor("query"), query)

executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[your_query],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
