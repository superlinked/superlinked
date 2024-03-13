Module superlinked.framework.dsl.source.in_memory_source
========================================================

Classes
-------

`InMemorySource(schema: ~SchemaObjectT, parser: superlinked.framework.common.parser.data_parser.DataParser | None = None)`
:   InMemorySource represents a source of data, where you can put your data. This will supply
    the index with the data it needs to index and search in.
    
    Initialize the InMemorySource.
    
    Args:
        schema (IdSchemaObject): The schema object.
        parser (DataParser | None, optional): The data parser. Defaults to JsonParser if None is supplied.
    
    Raises:
        InitializationException: If the schema is not an instance of SchemaObject.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.source.source.Source
    * abc.ABC
    * typing.Generic

    ### Methods

    `put(self, data: list[SourceTypeT]) ‑> None`
    :   Put data into the InMemorySource. This operation can take time as the vectorisation
        of your data happens here.
        
        Args:
            data (list[SourceTypeT]): The data to put.