Module superlinked.framework.dsl.app.rest.rest_app
==================================================

Classes
-------

`RestApp(sources: Sequence[superlinked.framework.dsl.source.rest_source.RestSource | superlinked.framework.dsl.source.data_loader_source.DataLoaderSource], queries: Sequence[superlinked.framework.dsl.executor.rest.rest_configuration.RestQuery], endpoint_configuration: superlinked.framework.dsl.executor.rest.rest_configuration.RestEndpointConfiguration, online_executor: superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryExecutor)`
:   Rest implementation of the App class.
    
    Initialize the RestApp from a RestExecutor.
    
    Args:
        sources (Sequence[RestSource | DataLoaderSource]): The list of sources, which can be either
            RestSource or DataLoaderSource.
        queries (Sequence[RestQuery]): The list of queries to be executed by the RestApp.
        endpoint_configuration (RestEndpointConfiguration): The configuration for the REST endpoints.
        online_executor (InMemoryExecutor): The in-memory executor that will be used to run the app.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.app.app.App
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `data_loader_sources: Sequence[superlinked.framework.dsl.source.data_loader_source.DataLoaderSource]`
    :   Property that returns the list of DataLoaderSource instances associated with the RestApp.
        
        Returns:
            Sequence[DataLoaderSource]: A sequence of DataLoaderSource instances.

    `handler: superlinked.framework.dsl.executor.rest.rest_handler.RestHandler`
    :   Property that returns the RestHandler instance associated with the RestApp.
        
        Returns:
            RestHandler: An instance of RestHandler.

    `online_app: superlinked.framework.dsl.app.in_memory.in_memory_app.InMemoryApp`
    :   Property that returns the InMemoryApp instance associated with the RestApp.
        
        Returns:
            InMemoryApp: An instance of InMemoryApp.