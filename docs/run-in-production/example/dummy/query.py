from superlinked import framework as sl

from .index import index, text_space, your_schema

query = (
    sl.Query(index)
    .find(your_schema)
    .similar(
        text_space.text,
        sl.Param("query_text"),
    )
    .select_all()
)
