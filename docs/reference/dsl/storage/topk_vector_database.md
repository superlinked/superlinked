Module superlinked.framework.dsl.storage.topk_vector_database
=============================================================

Classes
-------

`TopKVectorDatabase(api_key: str, region: str, https: bool = True, host: str = 'topk.io', default_query_limit: int = 10)`
:   TopK implementation of the VectorDatabase.
    This class provides a TopK-based vector database connector.
    
    Initialize the TopKVectorDatabase.
    Args:
        api_key (str): The API key for the TopK server.
        region (str): The region of the TopK server.
        https (bool): Whether to use HTTPS for the TopK server.
        host (str): The host of the TopK server.
        default_query_limit (int): Default vector search limit, set to TopK's default of 10.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic