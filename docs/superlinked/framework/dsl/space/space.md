Module superlinked.framework.dsl.space.space
============================================

Classes
-------

`Space()`
:   Abstract base class for a space.
    
    This class defines the interface for a space in the context of the application.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * superlinked.framework.dsl.space.recency_space.RecencySpace
    * superlinked.framework.dsl.space.text_similarity_space.TextSimilaritySpace

`SpaceFieldSet(space: Space, fields: set[SchemaField])`
:   A class representing a set of fields in a space.
    
    Attributes:
        space (Space): The space.
        fields (set[SchemaField]): The set of fields.