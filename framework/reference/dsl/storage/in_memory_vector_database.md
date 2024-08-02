Module superlinked.framework.dsl.storage.in_memory_vector_database
==================================================================

Classes
-------

`InMemoryVectorDatabase(default_query_limit: int = -1)`
:   In-memory implementation of the VectorDatabase.
    
    This class provides an in-memory vector database connector, which is useful for testing
    and development purposes.
    
    Initialize the InMemoryVectorDatabase.
    
    Args:
        default_query_limit (int): The default limit for query results. A value of -1 indicates no limit.
    
    Sets up an in-memory vector DB connector for testing and development.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic