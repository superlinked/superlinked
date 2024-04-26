Module superlinked.framework.dsl.space.categorical_similarity_space
===================================================================

Classes
-------

`CategoricalSimilaritySpace(category_input: superlinked.framework.common.schema.schema_object.String | list[superlinked.framework.common.schema.schema_object.String], categories: list[str], negative_filter: float = 0.0, uncategorized_as_category: bool = True, category_separator: str | None = None)`
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
    
    Attributes:
        category_input (Union[String, List[String]]): The schema field containing input
            category or categories to be considered in the similarity space. Input contains
            either a single category, or multiple categories separated by `category_separator`.
        categories (List[str]): A list of categories that defines the dimensionality of the
            one-hot encoded vector. Any category not listed is considered as 'other'.
        negative_filter (float): A value to represent unmatched categories in the one-hot vector.
            Instead of using 0, which typically represents the absence of a category, this allows
            for a different representation - resulting in effectively filtering out items that has
            non-matching categories.
        uncategorized_as_category (bool): If set to False, the similarity between other categories will be
            set to 0, or negative_filter if set. By this we can control if a category_input not in
            categories will be similar to other category_inputs not in categories. Note that the same
            category_inputs not in categories will not be similar to each other either.
        category_separator (str | None): The delimiter used to separate multiple categories within a
            single input field. This is relevant only when `category_input` is expected to contain
            multiple categories.
    
    Raises:
        InvalidSchemaException: If a schema object does not have a corresponding node in the
            similarity space.
    
    Initializes a new instance of the CategoricalSimilaritySpace.
    
    This constructor sets up the space with the necessary configurations to encode and measure categorical
    similarity based on the provided parameters.
    
    Args:
        category_input (String | list[String]): The schema field(s) that contain the input category or categories.
            This can be a single category field or multiple fields, coming from different schemas.
            Multilabel instances should be present in a single SchemaField, separated by the `category_separator`
            character.
        categories (list[str]): A list of all the recognized categories. Categories not included in this list will
            be treated as 'other', unless `uncategorized_as_category` is False.
        negative_filter (float, optional): A value used to represent unmatched categories in the encoding process.
            This allows for a penalizing non-matching categories - in contrast to them contributing 0 to similarity,
             it is possible to influence the similarity score negatively. Defaults to 0.0.
        uncategorized_as_category (bool, optional): Determines whether categories not listed in `categories` should
            be treated as a distinct 'other' category. Defaults to True.
        category_separator (str | None, optional): The delimiter used to separate multiple categories within a
            single input field. Defaults to None effectively meaning the whole text is the category.
    
    Raises:
        InvalidSchemaException: If a schema object does not have a corresponding node in the similarity space,
        indicating a configuration or implementation error.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC

    ### Instance variables

    `category: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `category_separator: str | None`
    :

    `uncategorized_as_category: bool`
    :