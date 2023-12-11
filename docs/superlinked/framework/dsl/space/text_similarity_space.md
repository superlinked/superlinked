Module superlinked.framework.dsl.space.text_similarity_space
============================================================

Functions
---------

    
`chunk(text: superlinked.framework.common.schema.schema_object.String, chunk_size: int | None = None, chunk_overlap: int | None = None) ‑> superlinked.framework.common.dag.chunking_node.ChunkingNode`
:   Create smaller chunks from the given text, a String SchemaFieldObject. It is helpful when you search
    for more granular information in your text corpus. It is recommended to try different chunk_sizes to
    find what fits best your use-case. Chunking respects word boundaries.
    
    Args:
        text (String): The text to chunk.
        chunk_size (int | None, optional): The maximum size of each chunk in characters. Defaults to None.
        chunk_overlap (int | None, optional): The maximum overlap between chunks in characters. Defaults to None.
    
    Returns:
        ChunkingNode: The chunking node.

Classes
-------

`TextSimilaritySpace(text: superlinked.framework.common.schema.schema_object.String | superlinked.framework.common.dag.chunking_node.ChunkingNode | list[superlinked.framework.common.schema.schema_object.String | superlinked.framework.common.dag.chunking_node.ChunkingNode], model: str)`
:   A text similarity space is used to create vectors from documents in order to search in them
    later on. We only support (SentenceTransformers)[https://www.sbert.net/] models as they have
    finetuned pooling to encode longer text sequences most efficiently.
    
    Initialize the TextSimilaritySpace.
    
    Args:
        text (TextInput | list[TextInput]): The Text input or a list of Text inputs.
        It is a SchemaFieldObject (String), not a regular python string.
        model (str): The model used for text similarity.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC