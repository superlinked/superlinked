Module superlinked.framework.dsl.executor.interactive.interactive_executor
==========================================================================

Classes
-------

`InteractiveExecutor(sources: Sequence[InteractiveSourceT], indices: Sequence[Index], vector_database: VectorDatabase | None = None, context_data: Mapping[str, Mapping[str, ContextValue]] | None = None)`
:   Interactive implementation of the Executor class. Supply it with the sources through which
    your data is received, the indices indicating the desired vector spaces, and optionally a vector database.
    The executor will create the spaces optimized for search.
    
    Initialize the InteractiveExecutor.
    Args:
        sources (list[InteractiveSourceT]): List of interactive sources.
        indices (list[Index]): List of indices.
        vector_database: (VectorDatabase | None): Vector database instance. Defaults to InMemoryVectorDatabase.
        context_data (Mapping[str, Mapping[str, ContextValue]] | None):
            Context data for execution. Defaults to None.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.executor.Executor
    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryExecutor

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.app.interactive.interactive_app.InteractiveApp`
    :   Run the InteractiveExecutor. It returns an app that can accept queries.
        Returns:
            InteractiveApp: An instance of InteractiveApp.