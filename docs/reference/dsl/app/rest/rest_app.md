Module superlinked.framework.dsl.app.rest.rest_app
==================================================

Classes
-------

`RestApp(sources: collections.abc.Sequence[superlinked.framework.dsl.source.rest_source.RestSource | superlinked.framework.dsl.source.data_loader_source.DataLoaderSource], indices: collections.abc.Sequence[superlinked.framework.dsl.index.index.Index], queries: collections.abc.Sequence[superlinked.framework.dsl.executor.rest.rest_configuration.RestQuery], vector_database: superlinked.framework.dsl.storage.vector_database.VectorDatabase, context: superlinked.framework.common.dag.context.ExecutionContext, endpoint_configuration: superlinked.framework.dsl.executor.rest.rest_configuration.RestEndpointConfiguration)`
:   Rest implementation of the App class.
    
    Initialize the RestApp from a RestExecutor.
    
    Args:
        sources (Sequence[RestSource | DataLoaderSource]): The list of sources, which can be either
            RestSource or DataLoaderSource.
        indices (Sequence[Index]): The list of indices to be used by the RestApp.
        queries (Sequence[RestQuery]): The list of queries to be executed by the RestApp.
        vector_database (VectorDatabase): The vector database instance to be used by the RestApp.
        context (ExecutionContext): The execution context for the RestApp.
        endpoint_configuration (RestEndpointConfiguration): The configuration for the REST endpoints.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.app.online.online_app.OnlineApp
    * superlinked.framework.dsl.app.app.App
    * abc.ABC
    * typing.Generic
    * superlinked.framework.dsl.query.query_mixin.QueryMixin

    ### Instance variables

    `data_loader_sources: collections.abc.Sequence[superlinked.framework.dsl.source.data_loader_source.DataLoaderSource]`
    :   Property that returns the list of DataLoaderSource instances associated with the RestApp.
        
        Returns:
            Sequence[DataLoaderSource]: A sequence of DataLoaderSource instances.

    `handler: superlinked.framework.dsl.executor.rest.rest_handler.RestHandler`
    :   Property that returns the RestHandler instance associated with the RestApp.
        
        Returns:
            RestHandler: An instance of RestHandler.