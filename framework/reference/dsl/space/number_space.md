Module superlinked.framework.dsl.space.number_space
===================================================

Classes
-------

`NumberSpace(number: superlinked.framework.common.schema.schema_object.Number | list[superlinked.framework.common.schema.schema_object.Number], min_value: int | float, max_value: int | float, mode: superlinked.framework.common.embedding.number_embedding.Mode, scale: superlinked.framework.common.embedding.number_embedding.Scale = LinearScale(), aggregation_mode: superlinked.framework.common.space.aggregation.InputAggregationMode = InputAggregationMode.INPUT_AVERAGE, negative_filter: float = 0.0)`
:   NumberSpace is used to encode numerical values within a specified range.
    The range is defined by the min_value and max_value parameters.
    The preference can be controlled by the mode parameter.
    
    Note: In similar mode you MUST add a similar clause to the query or it will raise.
    
    Attributes:
        number (SpaceFieldSet): A set of Number objects.
            It is a SchemaFieldObject not regular python ints or floats.
        min_value (float | int): This represents the minimum boundary. Any number lower than
            this will be considered as this minimum value. It can be either a float or an integer.
            It must larger or equal to 0 in case of scale=LogarithmicScale(base).
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
            It cannot be 0 in case of scale=LogarithmicScale(base).
        mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
            Similar mode expects a .similar on the query, otherwise it will default to maximum.
        scale (Scale): The scaling of the number embedding.
            Possible values are: LinearScale(), and LogarithmicScale(base).
            LogarithmicScale base must be larger than 1. It defaults to LinearScale().
        aggregation_mode (InputAggregationMode): The  aggregation mode of the number embedding.
            Possible values are: maximum, minimum and average.
        negative_filter (float): This is a value that will be set for everything that is equal or
            lower than the min_value. It can be a float. It defaults to 0 (No effect)
    
    Raises:
        InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
            Or the min_value is bigger than the max value, or the negative filter bigger than 0
        InvalidSchemaException: If there's no node corresponding to a given schema.
    
    Initializes the NumberSpace object.
    
    Attributes:
        number (SpaceFieldSet): A set of Number objects.
            It is a SchemaFieldObject not regular python ints or floats.
        min_value (float | int): This represents the minimum boundary. Any number lower than
            this will be considered as this minimum value. It can be either a float or an integer.
            It must larger or equal to 0 in case of scale=LogarithmicScale(base).
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
            It cannot be 0 in case of scale=LogarithmicScale(base).
        mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
            Similar mode expects a .similar on the query, otherwise it will default to maximum.
        scale (Scale): The scaling of the number embedding.
            Possible values are: LinearScale(), and LogarithmicScale(base).
            LogarithmicScale base must be larger than 1. It defaults to LinearScale().
        aggregation_mode (InputAggregationMode): The  aggregation mode of the number embedding.
            Possible values are: maximum, minimum and average.
        negative_filter (float): This is a value that will be set for everything that is equal or
            lower than the min_value. It can be a float. It defaults to 0 (No effect)
    
     Raises:
        InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
            Or the min_value is bigger than the max value, or the negative filter bigger than 0
        InvalidSchemaException: If there's no node corresponding to a given schema.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC

    ### Instance variables

    `annotation: str`
    :