Module superlinked.framework.dsl.executor.rest.rest_executor
============================================================

Classes
-------

`RestExecutor(sources: Sequence[RestSource | DataLoaderSource], indices: Sequence[Index], queries: Sequence[RestQuery], vector_database: VectorDatabase, endpoint_configuration: RestEndpointConfiguration | None = None, context_data: Mapping[str, Mapping[str, ContextValue]] | None = None)`
:   The RestExecutor is a subclass of the Executor base class. It encapsulates all the parameters required for
    the REST application. It also instantiates an InMemoryExecutor for data storage purposes.
    
    Initialize the RestExecutor.
    Attributes:
        sources: Sequence[RestSource | DataLoaderSource]: A sequence of rest or data loader sources.
        indices (Sequence[Index]): A sequence of indices.
        queries (Sequence[RestQuery]): A sequence of executable queries.
        vector_database (VectorDatabase) Vector database instance.
        endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.executor.Executor
    * abc.ABC
    * typing.Generic

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.app.rest.rest_app.RestApp`
    :   Run the RestExecutor. It returns an app that will create rest endpoints.
        
        Returns:
            RestApp: An instance of RestApp.