Module superlinked.framework.dsl.executor.rest.rest_executor
============================================================

Classes
-------

`RestApp(executor: RestExecutor)`
:   Rest implementation of the App class.
    
    Attributes:
        executor (RestExecutor): An instance of RestExecutor.
    
    Initialize the RestApp from an RestExecutor.
    
    Args:
        executor (RestExecutor): An instance of RestExecutor.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.executor.App
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `data_loader_sources: collections.abc.Sequence[superlinked.framework.dsl.source.data_loader_source.DataLoaderSource]`
    :   Property that returns the list of DataLoaderSource instances associated with the RestApp.
        
        Returns:
            Sequence[DataLoaderSource]: A sequence of DataLoaderSource instances.

    `handler: superlinked.framework.dsl.executor.rest.rest_handler.RestHandler`
    :   Property that returns the RestHandler instance associated with the RestApp.
        
        Returns:
            RestHandler: An instance of RestHandler.

    `online_app: superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryApp`
    :   Property that returns the InMemoryApp instance associated with the RestApp.
        
        Returns:
            InMemoryApp: An instance of InMemoryApp.

`RestExecutor(sources: Sequence[RestSource | DataLoaderSource], indices: Sequence[Index], queries: Sequence[RestQuery], vector_database: VectorDatabase, endpoint_configuration: RestEndpointConfiguration | None = None, context_data: Mapping[str, Mapping[str, ContextValue]] | None = None)`
:   The RestExecutor is a subclass of the Executor base class. It encapsulates all the parameters required for
    the REST application. It also instantiates an InMemoryExecutor for data storage purposes.
    
    Attributes:
        sources (Sequence[RestSource]): A sequence of rest sources that has information about the schema.
        indices (Sequence[Index]): A sequence of indices.
        queries (Sequence[RestQuery]): A sequence of executable queries.
        endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.
    
    Initialize the RestExecutor.
    Attributes:
        sources (Sequence[RestSource]): A sequence ofRest sources that has information about the schema.
        indices (Sequence[Index]): A sequence of indices.
        queries (Sequence[RestQuery]): A sequence ofexecutable queries.
        vector_database (VectorDatabase): Vector database instance.
        endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.executor.Executor
    * abc.ABC
    * typing.Generic

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.executor.rest.rest_executor.RestApp`
    :   Run the RestExecutor. It returns an app that will create rest endpoints.
        
        Returns:
            RestApp: An instance of RestApp.