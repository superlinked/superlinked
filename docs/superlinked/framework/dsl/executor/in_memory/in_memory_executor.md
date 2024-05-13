Module superlinked.framework.dsl.executor.in_memory.in_memory_executor
======================================================================

Classes
-------

`InMemoryApp(executor: superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryExecutor)`
:   In-memory implementation of the App class.
    
    Attributes:
        executor (InMemoryExecutor): An instance of InMemoryExecutor.
    
    Initialize the InMemoryApp from an InMemoryExecutor.
    
    Args:
        executor (InMemoryExecutor): An instance of InMemoryExecutor.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.executor.App
    * abc.ABC
    * typing.Generic

    ### Methods

    `persist(self, writer: superlinked.framework.storage.persistable_dict.ObjectWriter) ‑> None`
    :

    `query(self, query_obj: superlinked.framework.dsl.query.query.QueryObj, **params: Any) ‑> superlinked.framework.dsl.query.result.Result`
    :   Execute a query. Example:
        ```
        query = (
            Query(relevance_index, weights=[{"relevance_space": Param("relevance_weight")}])
            .find(paragraph)
            .with_vector(user, Param("user_id"))
            .similar(relevance_space.text, Param("query_text"), weight=Param("query_weight"))
        )
        
        result = app.query(
            query, query_text="Pear", user_id="some_user", relevance_weight=1, query_weight=2
        )
        ```
        
        Args:
            query_obj (QueryObj): The query object.
            **params: Additional parameters.
        
        Returns:
            Result:  The result of the query.
        
        Raises:
            QueryException: If the query index is not amongst the executor's indices.

    `restore(self, reader: superlinked.framework.storage.persistable_dict.ObjectReader) ‑> None`
    :

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
        context (Mapping[str, Mapping[str, Any]]): Context mapping.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.executor.executor.Executor
    * superlinked.framework.dsl.executor.runnable.Runnable
    * typing.Generic
    * abc.ABC

    ### Methods

    `run(self) ‑> superlinked.framework.dsl.executor.in_memory.in_memory_executor.InMemoryApp`
    :   Run the InMemoryExecutor. It returns an app that can accept queries.
        
        Returns:
            InMemoryApp: An instance of InMemoryApp.