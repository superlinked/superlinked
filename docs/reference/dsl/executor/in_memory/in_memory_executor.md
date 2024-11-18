Module superlinked.framework.dsl.executor.in_memory.in_memory_executor
======================================================================

Classes
-------

`InMemoryExecutor(sources: InMemorySource | Sequence[InMemorySource], indices: Index | Sequence[Index], context_data: Mapping[str, Mapping[str, ContextValue]] | None = None)`
:   Initialize the InMemoryExecutor.
    
    The InMemoryExecutor provides an in-memory implementation for executing queries against indexed data.
    It creates optimized vector spaces based on the provided indices
    and allows querying data from in-memory sources.
    
    Args:
        sources (InMemorySource | Sequence[InMemorySource]): One or more in-memory data sources to query against.
            Can be a single source or sequence of sources.
        indices (Index | Sequence[Index]): One or more indices that define the vector spaces.
            Can be a single index or sequence of indices.
        context_data (Mapping[str, Mapping[str, ContextValue]] | None, optional): Additional context data
            for execution. The outer mapping key represents the context name, inner mapping contains
            key-value pairs for that context. Defaults to None.
    
    Initialize the InMemoryExecutor.
    
    The InMemoryExecutor provides an in-memory implementation for executing queries against indexed data.
    It creates optimized vector spaces based on the provided indices
    and allows querying data from in-memory sources.
    
    Args:
        sources (InMemorySource | Sequence[InMemorySource]): One or more in-memory data sources to query against.
            Can be a single source or sequence of sources.
        indices (Index | Sequence[Index]): One or more indices that define the vector spaces.
            Can be a single index or sequence of indices.
        context_data (Mapping[str, Mapping[str, ContextValue]] | None, optional): Additional context data
            for execution. The outer mapping key represents the context name, inner mapping contains
            key-value pairs for that context. Defaults to None.

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