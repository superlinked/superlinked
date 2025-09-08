Module superlinked.framework.dsl.space.categorical_similarity_space
===================================================================

Classes
-------

`CategoricalSimilaritySpace(category_input: superlinked.framework.common.schema.schema_object.String | superlinked.framework.common.schema.schema_object.StringList | None | list[superlinked.framework.common.schema.schema_object.String | superlinked.framework.common.schema.schema_object.StringList | None], categories: list[str], negative_filter: float = 0.0, uncategorized_as_category: bool = True, salt: str | None = None)`
:   Represents a space for encoding categorical similarity.
    
    A CategoricalSimilaritySpace is designed to measure the similarity between items that
    are grouped into a finite number of textual categories. The categories are represented
    in an n-hot encoded vector, with the option to apply a negative filter for unmatched
    categories, enhancing the distinction between matching and non-matching category items.
    Negative_filter allows for filtering out unmatched categories, by setting
    it to a large negative value, effectively resulting in large negative similarity between
    non-matching category items. A category input not present in categories will be encoded
    as `other` category. These categories will be similar to each other by default. Set
    uncategorized_as_category parameter to False in order to suppress this behavior - this
    way other categories are not similar to each other in any case - not even to the same
    `other` category. To make that specific category value similar to only the same category
    items, consider adding it to `categories`.
    
    Initializes a new instance of the CategoricalSimilaritySpace.
    
    This constructor sets up the space with the necessary configurations to encode and measure categorical
    similarity based on the provided parameters.
    
    Args:
        category_input (StringList | String | list[String | StringList]):
        The schema field containing input categories to be considered in the similarity space.
        Input contains one or more categories in a list if `StringList` is provided.
        If `String` is provided, then the input must be a single value.
        categories (list[str]): A list of all the recognized categories. Categories not included in this list will
            be treated as 'other', unless `uncategorized_as_category` is False.
        negative_filter (float, optional): A value used to represent unmatched categories in the encoding process.
            This allows for a penalizing non-matching categories - in contrast to them contributing 0 to similarity,
             it is possible to influence the similarity score negatively. Defaults to 0.0.
        uncategorized_as_category (bool, optional): Determines whether categories not listed in `categories` should
            be treated as a distinct 'other' category. Defaults to True.
        salt: (str | None, optional): Enables the creation of identical spaces to allow
            different weighted event definitions with them.
    
    Raises:
        InvalidInputException: If a schema object does not have a corresponding node in the similarity space,
        indicating a configuration or implementation error.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * superlinked.framework.common.space.interface.has_transformation_config.HasTransformationConfig
    * superlinked.framework.common.interface.has_length.HasLength
    * typing.Generic
    * superlinked.framework.dsl.space.has_space_field_set.HasSpaceFieldSet
    * abc.ABC

    ### Instance variables

    `category: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `space_field_set: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `transformation_config: superlinked.framework.common.space.config.transformation_config.TransformationConfig[superlinked.framework.common.data_types.Vector, list[str]]`
    :

    `uncategorized_as_category: bool`
    :