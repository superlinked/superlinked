Module superlinked.framework.dsl.space.categorical_similarity_space
===================================================================

Classes
-------

`CategoricalSimilaritySpace(category_input: superlinked.framework.common.schema.schema_object.String | list[superlinked.framework.common.schema.schema_object.String], categories: list[str], negative_filter: float = 0.0, uncategorised_as_category: bool = True)`
:   Represents a space for encoding categorical similarity.
    
    A CategoricalSimilaritySpace is designed to measure the similarity between items that
    are grouped into a finite number of textual categories. The categories are represented
    in a one-hot encoded vector, with the option to apply a negative filter for unmatched
    categories. Negative_filter allows for filtering out unmatched categories, by setting
    it to a large negative value, effectively resulting in large negative similarity between
    non-matching category items. A category input not present in categories will be encoded
    as other category. These categories will be similar to each other by default. Set
    uncategorised_as_category parameter to False in order to suppress this behaviour.
    
    Attributes:
        category_input (Union[String, List[String]]): The schema field containing input
            category or categories to be considered in the similarity space.
        categories (List[str]): A list of categories that defines the dimensionality of the
            one-hot encoded vector. Any category not listed is considered as 'other'.
        negative_filter (float): A value to represent unmatched categories in the one-hot vector.
            Instead of using 0, which typically represents the absence of a category, this allows
            for a different representation - resulting in effectively filtering out items that has
            non-matching categories.
        uncategorised_as_category (bool): If set to False, the similarity between other categories will be
            set to 0, or negative_filter if set. By this we can control if a category_input not in
            categories will be similar to other category_inputs not in categories. Note that the same
            category_inputs not in categories will not be similar to each other either.
    
    Raises:
        InvalidSchemaException: If a schema object does not have a corresponding node in the
            similarity space.
    
    Initialize the CategoricalSimilaritySpace.
    
    Args:
        category_input (String | list[String]): The category input Schema field.
        categories (list[str]): This controls the set of categories represented in the one-hot vector,
            else it falls into the other category. It is needed to control dimensionality.
        negative_filter (float): Not matched category vector elements are not initialized as 0,
            but as negative_filter

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC

    ### Instance variables

    `category: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `uncategorised_as_category: bool`
    :