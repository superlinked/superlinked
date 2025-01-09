from superlinked import framework as sl

from .index import car_schema, index
from .query import query

car_source: sl.RestSource = sl.RestSource(car_schema)

executor = sl.RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[sl.RestQuery(sl.RestDescriptor("query"), query)],
    vector_database=sl.InMemoryVectorDatabase(),
)

sl.SuperlinkedRegistry.register(executor)
