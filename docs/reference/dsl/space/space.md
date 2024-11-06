Module superlinked.framework.dsl.space.space
============================================

Classes
-------

`Space(fields: SpaceSchemaFieldT | list[SpaceSchemaFieldT], type_: type | TypeAlias)`
:   Abstract base class for a space.
    
    This class defines the interface for a space in the context of the application.

    ### Ancestors (in MRO)

    * superlinked.framework.common.space.interface.has_transformation_config.HasTransformationConfig
    * superlinked.framework.common.interface.has_length.HasLength
    * typing.Generic
    * abc.ABC

    ### Descendants

    * superlinked.framework.dsl.space.categorical_similarity_space.CategoricalSimilaritySpace
    * superlinked.framework.dsl.space.custom_space.CustomSpace
    * superlinked.framework.dsl.space.image_space.ImageSpace
    * superlinked.framework.dsl.space.number_space.NumberSpace
    * superlinked.framework.dsl.space.recency_space.RecencySpace
    * superlinked.framework.dsl.space.text_similarity_space.TextSimilaritySpace

    ### Instance variables

    `annotation: str`
    :

    `length: int`
    :