Module superlinked.framework.dsl.storage.qdrant_vector_database
===============================================================

Classes
-------

`QdrantVectorDatabase(url: str, api_key: str, default_query_limit: int = 10, search_algorithm: superlinked.framework.common.storage.search_index.search_algorithm.SearchAlgorithm = SearchAlgorithm.FLAT, vector_precision: superlinked.framework.common.precision.Precision = Precision.FLOAT16, client_params: collections.abc.Mapping[str, typing.Any] | None = None, **extra_params: Any)`
:   Qdrant implementation of the VectorDatabase.
    
    This class provides a Qdrant-based vector database connector.
    
    Initialize the QdrantVectorDatabase.
    
    Args:
        url (str): The url of the Qdrant server.
        api_key (str): The api key of the Qdrant cluster.
        default_query_limit (int): Default vector search limit, set to Qdrant's default of 10.
        vector_precision (Precision): Precision to use for storing vectors. Defaults to FLOAT16.
        client_params (Mapping[str, Any] | None): Additional parameters for the QdrantClient.
        These are passed directly to the QdrantClient constructor, so any valid QdrantClient
        parameter can be used. For example `{"prefer_grpc": True}`. Defaults to None.
        **extra_params (Any): Additional parameters for the Qdrant connection.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic