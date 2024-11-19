Module superlinked.framework.dsl.storage.qdrant_vector_database
===============================================================

Classes
-------

`QdrantVectorDatabase(url: str, api_key: str, default_query_limit: int = 10, **extra_params: Any)`
:   Qdrant implementation of the VectorDatabase.
    
    This class provides a Qdrant-based vector database connector.
    
    Initialize the QdrantVectorDatabase.
    
    Args:
        url (str): The url of the Qdrant server.
        api_key (str): The api key of the Qdrant cluster.
        default_query_limit (int): Default vector search limit, set to Qdrant's default of 10.
        **extra_params (Any): Additional parameters for the Qdrant connection.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic