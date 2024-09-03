from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query

from .index import index, text_space, your_schema

query = (
    Query(index)
    .find(your_schema)
    .similar(
        text_space.text,
        Param("query_text"),
    )
)
