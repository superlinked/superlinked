Module superlinked.framework.dsl.executor.executor
==================================================

Classes
-------

`App(executor: ExecutorT)`
:   Abstract base class for an App, a running executor that can for example do queries or ingest data.
    
    Initialize the App.
    
    Args:
        executor (ExecutorT): The executor instance.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryApp
    * superlinked.framework.dsl.executor.rest.rest_executor.RestApp

    ### Instance variables

    `executor: ~ExecutorT`
    :   Get the executor.
        
        Returns:
            ExecutorT: The executor instance.

    `storage_manager: superlinked.framework.common.storage_manager.storage_manager.StorageManager`
    :   Get the storage manager.
        
        Returns:
            StorageManager: The storage manager instance.

`Executor(sources: collections.abc.Sequence[~SourceT], indices: typing.Annotated[collections.abc.Sequence[superlinked.framework.dsl.index.index.Index], Is[TypeValidator.list_validator.validator]], vector_database: superlinked.framework.dsl.storage.vector_database.VectorDatabase, context: superlinked.framework.common.dag.context.ExecutionContext)`
:   Abstract base class for an executor.
    
    Initialize the Executor.
    
    Args:
        sources (list[SourceT]): The list of sources.
        indices (list[Index]): The list of indices.
        vector_database (VectorDatabase): The vector database which the executor will use.
        context (Mapping[str, Mapping[str, Any]]): The context mapping.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryExecutor
    * superlinked.framework.dsl.executor.rest.rest_executor.RestExecutor

    ### Instance variables

    `context: superlinked.framework.common.dag.context.ExecutionContext`
    :   Get the context.
        
        Returns:
            Mapping[str, Mapping[str, Any]]: The context mapping.

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.executor.executor.App[typing.Self]`
    :   Abstract method to run the executor.
        
        Returns:
            App[Self]: An instance of App.