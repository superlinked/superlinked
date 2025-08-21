Module superlinked.framework.dsl.space.image_space
==================================================

Classes
-------

`ImageSpace(image: superlinked.framework.common.schema.schema_object.Blob | superlinked.framework.common.schema.schema_object.DescribedBlob | None | collections.abc.Sequence[superlinked.framework.common.schema.schema_object.Blob | superlinked.framework.common.schema.schema_object.DescribedBlob | None], model: str = 'clip-ViT-B-32', model_cache_dir: pathlib.Path | None = None, model_handler: superlinked.framework.common.space.embedding.model_based.model_handler.ModelHandler = ModelHandler.SENTENCE_TRANSFORMERS, embedding_engine_config: superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config.EmbeddingEngineConfig | None = None)`
:   Initialize the ImageSpace instance for generating vector representations
    from images, supporting models from the SentenceTransformers and OpenCLIP projects.
    
    Initialize the ImageSpace instance for generating vector representations
    from images, supporting models from the OpenCLIP project.
    
    Args:
        image (Blob | DescribedBlob | Sequence[Blob | DescribedBlob]):
            The image content as a Blob or DescribedBlob (write image+description), or a sequence of them.
        model (str, optional): The model identifier for generating image embeddings.
            Defaults to "clip-ViT-B-32".
        model_handler (ModelHandler, optional): The handler for the model,
            defaults to ModelHandler.SENTENCE_TRANSFORMERS.
        model_cache_dir (Path | None, optional): Directory to cache downloaded models.
            If None, uses the default cache directory. Defaults to None.
        embedding_engine_config (EmbeddingEngineConfig, optional): Configuration for the embedding engine.
            Defaults to EmbeddingEngineConfig().
    
    Raises:
        InvalidInputException: If the image and description fields are not
            from the same schema.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * superlinked.framework.common.space.interface.has_transformation_config.HasTransformationConfig
    * superlinked.framework.common.interface.has_length.HasLength
    * typing.Generic
    * abc.ABC

    ### Instance variables

    `transformation_config: superlinked.framework.common.space.config.transformation_config.TransformationConfig[superlinked.framework.common.data_types.Vector, superlinked.framework.common.schema.image_data.ImageData]`
    :