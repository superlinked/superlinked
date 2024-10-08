Module superlinked.framework.dsl.executor.in_memory.in_memory_executor
======================================================================

Classes
-------

`InMemoryExecutor(sources: Sequence[InMemorySource], indices: Sequence[Index], context_data: Mapping[str, Mapping[str, ContextValue]] | None = None)`
:   In-memory implementation of the Executor class. Supply it with the sources through which
    your data is received, and the indices indicating the desired vector spaces, and the executor will
    create the spaces optimized for search.
    Attributes:
        sources (list[InMemorySource]): List of in-memory sources.
        indices (list[Index]): List of indices.
    
    Initialize the InMemoryExecutor.
    Args:
        sources (list[InMemorySource]): List of in-memory sources.
        indices (list[Index]): List of indices.
        context_data (Mapping[str, Mapping[str, ContextValue]] | None):
            Context data for execution. Defaults to None.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.interactive.interactive_executor.InteractiveExecutor
    * superlinked.framework.dsl.executor.executor.Executor
    * abc.ABC
    * typing.Generic

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.app.in_memory.in_memory_app.InMemoryApp`
    :   Run the InMemoryExecutor. It returns an app that can accept queries.
        Returns:
            InMemoryApp: An instance of InMemoryApp.