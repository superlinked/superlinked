Module superlinked.framework.dsl.app.interactive.interactive_app
================================================================

Classes
-------

`InteractiveApp(sources: collections.abc.Sequence[superlinked.framework.dsl.source.interactive_source.InteractiveSource], indices: collections.abc.Sequence[superlinked.framework.dsl.index.index.Index], vector_database: superlinked.framework.dsl.storage.vector_database.VectorDatabase, context: superlinked.framework.common.dag.context.ExecutionContext, init_search_indices: bool = True)`
:   Interactive implementation of the App class.
    
    Initialize the InteractiveApp from an InteractiveExecutor.
    Args:
        sources (list[InteractiveSource]): List of interactive sources.
        indices (list[Index]): List of indices.
        vector_database (VectorDatabase | None): Vector database instance. Defaults to InMemory.
        context (Mapping[str, Mapping[str, Any]]): Context mapping.
        init_search_indices (bool): Decides if the search indices need to be created. Defaults to True.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.app.online.online_app.OnlineApp
    * superlinked.framework.dsl.app.app.App
    * abc.ABC
    * typing.Generic
    * superlinked.framework.dsl.query.query_mixin.QueryMixin

    ### Descendants

    * superlinked.framework.dsl.app.in_memory.in_memory_app.InMemoryApp