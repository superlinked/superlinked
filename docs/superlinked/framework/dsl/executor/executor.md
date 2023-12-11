Module superlinked.framework.dsl.executor.executor
==================================================

Classes
-------

`App(executor: ExecutorT, entity_store: EntityStore, object_store: ObjectStore)`
:   Abstract base class for an App, a running executor that can for example do queries or ingest data.
    
    Initialize the App.
    
    Args:
        executor (TExecutor): The executor instance.
        entity_store (EntityStore): The entity store instance.
        object_store (ObjectStore): The object store instance.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryApp

    ### Instance variables

    `executor: ~ExecutorT`
    :   Get the executor.
        
        Returns:
            ExecutorT: The executor instance.

    `store_manager: superlinked.framework.storage.entity_store_manager.EntityStoreManager`
    :   Get the store manager.
        
        Returns:
            EntityStoreManager: The store manager instance.

`Executor(sources: list[SourceT], indices: list[Index], context: ExecutionContext)`
:   Abstract base class for an executor.
    
    Initialize the Executor.
    
    Args:
        sources (list[SourceT]): The list of sources.
        indices (list[Index]): The list of indices.
        context (Mapping[str, Mapping[str, Any]]): The context mapping.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryExecutor

    ### Instance variables

    `context`
    :   Get the context.
        
        Returns:
            Mapping[str, Mapping[str, Any]]: The context mapping.

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.executor.executor.App[typing_extensions.Self]`
    :   Abstract method to run the executor.
        
        Returns:
            App[Self]: An instance of App.