Module superlinked.framework.dsl.space.categorical_similarity_space
===================================================================

Classes
-------

`CategoricalSimilaritySpace(category_input: superlinked.framework.common.schema.schema_object.String | list[superlinked.framework.common.schema.schema_object.String], categories: list[str], negative_filter: float = 0.0)`
:   A text similarity space is used to to reflect similarity between items grouped into a finite number of categories.
    Not necessarily just already grouped items: similarity in terms of scalars can also be expressed this way.
    Scalars need to be first grouped into bins, and from there the process is similar.
    
    Initialize the CategoricalSimilaritySpace.
    
    Args:
        category_input (String | list[String]): The category input
        categories (list[str]): This controls the set of categories represented in the one-hot vector,
            else it falls into the other category. It is needed to control dimensionality.
        negative_filter (float): Not matched category vector elements are not initialized as 0,
            but as negative_filter

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC