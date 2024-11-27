Module superlinked.framework.dsl.query.query_mixin
==================================================

Classes
-------

`QueryMixin()`
:   A mixin class that provides query execution capabilities for classes that include it.
    This class sets up the necessary infrastructure to execute queries on a set of indices
    using a storage manager.

    ### Descendants

    * superlinked.framework.dsl.app.online.online_app.OnlineApp

    ### Methods

    `query(self, query_descriptor: superlinked.framework.dsl.query.query_descriptor.QueryDescriptor, **params: Any) ‑> superlinked.framework.dsl.query.result.Result`
    :   Execute a query using the provided QueryDescriptor and additional parameters.
        
        Args:
            query_descriptor (QueryDescriptor): The query object containing the query details.
            **params (Any): Additional parameters for the query execution.
        
        Returns:
            Result: The result of the query execution.
        
        Raises:
            QueryException: If the query index is not found among the executor's indices.

    `setup_query_execution(self, indices: Sequence[superlinked.framework.dsl.index.index.Index]) ‑> None`
    :   Set up the query execution environment by initializing a mapping between indices
        and their corresponding QueryVectorFactory instances.
        
        Args:
            indices (Sequence[Index]): A sequence of Index instances to be used for query execution.
            storage_manager (StorageManager): The storage manager instance to be used.