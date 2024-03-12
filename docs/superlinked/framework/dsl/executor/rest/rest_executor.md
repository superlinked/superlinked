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

    `rest_app: fastapi.applications.FastAPI`
    :   Property that returns the REST application instance.
        
        This property is used to get the instance of the REST application that has been created
        with the defined sources and queries. The application instance is of type FastAPI and
        it is used to handle the REST API requests.
        
        Returns:
            FastAPI: The instance of the REST application.

`RestExecutor(sources: list[RestSource], indices: list[Index], queries: list[RestQuery], endpoint_configuration: RestEndpointConfiguration | None = None, context_data: Mapping[str, Mapping[str, ContextValue]] | None = None)`
:   The RestExecutor is a subclass of the Executor base class. It encapsulates all the parameters required for
    the REST application. It also instantiates an InMemoryExecutor for data storage purposes.
    
    Attributes:
        sources (list[RestSource]): List of Rest sources that has information about the schema.
        indices (list[Index]): List indices.
        queries (list[RestQuery]): List of executable queries.
        endpoint_configuration (RestEndpointConfiguration): Optional configuration for REST endpoints.
    
    Initialize the RestExecutor.
    
    Attributes:
        sources (list[RestSource]): List of Rest sources that has information about the schema.
        indices (list[Index]): List indices.
        queries (list[RestQuery]): List of executable queries.
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