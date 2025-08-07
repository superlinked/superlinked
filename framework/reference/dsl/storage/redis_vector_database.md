Module superlinked.framework.dsl.storage.redis_vector_database
==============================================================

Classes
-------

`RedisVectorDatabase(host: str, port: int, default_query_limit: int = 10, search_algorithm: superlinked.framework.common.storage.search_index.search_algorithm.SearchAlgorithm = SearchAlgorithm.FLAT, vector_precision: superlinked.framework.common.precision.Precision = Precision.FLOAT16, **extra_params: Any)`
:   Redis implementation of the VectorDatabase.
    
    This class provides a Redis-based vector database connector.
    
    Initialize the RedisVectorDatabase.
    
    Args:
        host (str): The hostname of the Redis server.
        port (int): The port number of the Redis server.
        default_query_limit (int): Default vector search limit, set to Redis's default of 10.
        search_algorithm (SearchAlgorithm): The algorithm to use for vector search. Defaults to FLAT.
        vector_precision (Precision): Precision to use for storing vectors. Defaults to FLOAT16.
        **extra_params (Any): Additional parameters for the Redis connection.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic