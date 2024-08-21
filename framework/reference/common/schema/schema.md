Module superlinked.framework.common.schema.schema
=================================================

Functions
---------

    
`schema(cls: type[T]) ‑> type[~T] | type[superlinked.framework.common.schema.schema.Schema]`
:   Use this decorator to annotate your class as a schema
    that can be used to represent your structured data.
    
    Schemas translate to entities in the embedding space
    that you can search by or search for.