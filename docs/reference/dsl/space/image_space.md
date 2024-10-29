Module superlinked.framework.dsl.space.image_space
==================================================

Classes
-------

`ImageSpace(image: superlinked.framework.common.schema.schema_object.Blob | superlinked.framework.common.schema.schema_object.DescribedBlob | collections.abc.Sequence[superlinked.framework.common.schema.schema_object.Blob | superlinked.framework.common.schema.schema_object.DescribedBlob], model: str = 'clip-ViT-B-32')`
:   Initialize the ImageSpace instance.
    
    This constructor sets up an ImageSpace, which is used to generate
    vector representations from images for search and retrieval tasks.
    It supports models from the (OpenCLIP)[https://github.com/mlfoundations/open_clip] project.
    
    Args:
        image (Blob): The image content encapsulated as a Blob object.
            This represents the raw image data to be processed.
        description (String, optional): A description of the image content.
            This should be a SchemaFieldObject of type String, not a standard
            Python string. It provides additional context for the image.
            If not provided, a default description field is used.
        model (str, optional): The identifier for the model used to generate
            image embeddings. Defaults to "clip-ViT-B-32". This model
            determines the method of embedding the image into a vector space.
    
    Raises:
        InvalidSpaceParamException: If the image and description fields
            do not belong to the same schema.
    
    Initialize the ImageSpace instance.
    
    This constructor sets up an ImageSpace, which is used to generate
    vector representations from images for search and retrieval tasks.
    It supports models from the (OpenCLIP)[https://github.com/mlfoundations/open_clip] project.
    
    Args:
        image (Blob): The image content encapsulated as a Blob object.
            This represents the raw image data to be processed.
        description (String, optional): A description of the image content.
            This should be a SchemaFieldObject of type String, not a standard
            Python string. It provides additional context for the image.
            If not provided, a default description field is used.
        model (str, optional): The identifier for the model used to generate
            image embeddings. Defaults to "clip-ViT-B-32". This model
            determines the method of embedding the image into a vector space.
    
    Raises:
        InvalidSpaceParamException: If the image and description fields
            do not belong to the same schema.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * superlinked.framework.common.space.interface.has_transformation_config.HasTransformationConfig
    * superlinked.framework.common.interface.has_length.HasLength
    * typing.Generic
    * abc.ABC

    ### Instance variables

    `annotation: str`
    :

    `transformation_config: superlinked.framework.common.space.config.transformation_config.TransformationConfig[superlinked.framework.common.data_types.Vector, superlinked.framework.common.schema.image_data.ImageData]`
    :

    ### Methods

    `get_node_id(self, schema_field: superlinked.framework.common.schema.schema_object.SchemaField) ‑> str`
    :