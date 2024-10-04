Module superlinked.framework.dsl.source.interactive_source
==========================================================

Classes
-------

`InteractiveSource(schema: ~IdSchemaObjectT, parser: Optional[superlinked.framework.common.parser.data_parser.DataParser[~IdSchemaObjectT, ~SourceTypeT]] = None)`
:   InteractiveSource represents a source of data, where you can put your data. This will supply
    the index with the data it needs to index and search in.
    
    Initialize the InteractiveSource.
    
    Args:
        schema (IdSchemaObject): The schema object.
        parser (DataParser | None, optional): The data parser. Defaults to JsonParser if None is supplied.
    
    Raises:
        InitializationException: If the schema is not an instance of SchemaObject.

    ### Ancestors (in MRO)

    * superlinked.framework.online.source.online_source.OnlineSource
    * superlinked.framework.common.observable.TransformerPublisher
    * superlinked.framework.common.source.source.Source
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.source.in_memory_source.InMemorySource

    ### Methods

    `put(self, data: Sequence[SourceTypeT]) ‑> None`
    :   Put data into the InteractiveSource. This operation can take time as the vectorization
        of your data happens here.
        
        Args:
            data (list[SourceTypeT]): The data to put.