Module superlinked.framework.dsl.app.online.online_app
======================================================

Classes
-------

`OnlineApp(sources: collections.abc.Sequence[~SourceT], indices: collections.abc.Sequence[superlinked.framework.dsl.index.index.Index], vector_database: superlinked.framework.dsl.storage.vector_database.VectorDatabase, context: superlinked.framework.common.dag.context.ExecutionContext)`
:   Manages the execution environment for online sources and indices.
    
    This class extends the base App class and incorporates the QueryMixin to handle
    query execution. It is designed to work with online sources and indices, providing
    the necessary setup and management for efficient data processing and querying.
    
    Initialize the OnlineApp with the given sources, indices, vector database, and execution context.
    
    Args:
        sources (Sequence[SourceT]): A sequence of data sources to be used by the application.
        indices (Sequence[Index]): A sequence of indices for data retrieval and storage.
        vector_database (VectorDatabase): The vector database instance for managing vector data.
        context (ExecutionContext): The execution context providing necessary runtime information.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.app.app.App
    * abc.ABC
    * typing.Generic
    * superlinked.framework.dsl.query.query_mixin.QueryMixin

    ### Descendants

    * superlinked.framework.dsl.app.in_memory.in_memory_app.InMemoryApp
    * superlinked.framework.dsl.app.rest.rest_app.RestApp