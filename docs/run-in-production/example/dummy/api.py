from superlinked import framework as sl

from .index import index, your_schema
from .query import query

your_source: sl.RestSource = sl.RestSource(your_schema)
your_query = sl.RestQuery(sl.RestDescriptor("query"), query)

executor = sl.RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[your_query],
    vector_database=sl.InMemoryVectorDatabase(),
)

sl.SuperlinkedRegistry.register(executor)
