Module superlinked.framework.dsl.space.custom_space
===================================================

Classes
-------

`CustomSpace(vector: superlinked.framework.common.schema.schema_object.Array | list[superlinked.framework.common.schema.schema_object.Array], length: int, normalization: superlinked.framework.common.space.normalization.Normalization = <superlinked.framework.common.space.normalization.L2Norm object>)`
:   CustomSpace is the instrument of ingesting your own vectors into Superlinked.
    This way you can use your own vectors right away. What you need to know: (you can use numbering too)
    - vectors need to have the same length
    - vectors will be L2Norm normalised to ensure weighting makes sense
    - weighting can be performed (query-time)
    - you are going to need an Array typed SchemaField to supply your data
    - the Array field will be able to parse any Sequence[float]
    
    Initialize the CustomSpace.
    
    Args:
        vector (Array | list[Array]): The input containing the vectors
        length (int): The length of inputs (should be the same for all inputs)

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC