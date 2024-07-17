Module superlinked.framework.dsl.app.in_memory.in_memory_app
============================================================

Classes
-------

`InMemoryApp(sources: collections.abc.Sequence[superlinked.framework.dsl.source.in_memory_source.InMemorySource], indices: collections.abc.Sequence[superlinked.framework.dsl.index.index.Index], vector_database: superlinked.framework.dsl.storage.vector_database.VectorDatabase, context: superlinked.framework.common.dag.context.ExecutionContext)`
:   In-memory implementation of the App class.
    
    Initialize the InMemoryApp from an InMemoryExecutor.
    Args:
        sources (list[InMemorySource]): List of in-memory sources.
        indices (list[Index]): List of indices.
        vector_database (VectorDatabase | None): Vector database instance. Defaults to InMemory.
        context (Mapping[str, Mapping[str, Any]]): Context mapping.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.app.app.App
    * abc.ABC
    * typing.Generic

    ### Methods

    `persist(self, serializer: superlinked.framework.storage.in_memory.object_serializer.ObjectSerializer) ‑> None`
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

    `restore(self, serializer: superlinked.framework.storage.in_memory.object_serializer.ObjectSerializer) ‑> None`
    :