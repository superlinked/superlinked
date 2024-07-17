Module superlinked.framework.dsl.storage.redis_vector_database
==============================================================

Classes
-------

`RedisVectorDatabase(host: str, port: int, **extra_params: Any)`
:   Redis implementation of the VectorDatabase.
    
    This class provides a Redis-based vector database connector.
    
    Initialize the RedisVectorDatabase.
    
    Args:
        host (str): The hostname of the Redis server.
        port (int): The port number of the Redis server.
        **extra_params (Any): Additional parameters for the Redis connection.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic