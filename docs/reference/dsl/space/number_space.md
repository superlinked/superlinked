Module superlinked.framework.dsl.space.number_space
===================================================

Classes
-------

`NumberSpace(number: superlinked.framework.common.schema.schema_object.Number | list[superlinked.framework.common.schema.schema_object.Number], min_value: float | int, max_value: float | int, mode: superlinked.framework.common.space.config.embedding.number_embedding_config.Mode, scale: superlinked.framework.common.space.config.embedding.number_embedding_config.Scale = LinearScale(), aggregation_mode: superlinked.framework.dsl.space.input_aggregation_mode.InputAggregationMode = InputAggregationMode.INPUT_AVERAGE, negative_filter: float = 0.0)`
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

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * superlinked.framework.common.space.interface.has_transformation_config.HasTransformationConfig
    * superlinked.framework.common.interface.has_length.HasLength
    * typing.Generic
    * superlinked.framework.common.interface.has_annotation.HasAnnotation
    * superlinked.framework.dsl.space.has_space_field_set.HasSpaceFieldSet
    * abc.ABC

    ### Instance variables

    `space_field_set: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `transformation_config: superlinked.framework.common.space.config.transformation_config.TransformationConfig[float, float]`
    :