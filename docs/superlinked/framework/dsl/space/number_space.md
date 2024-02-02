Module superlinked.framework.dsl.space.number_space
===================================================

Classes
-------

`NumberSpace(number: superlinked.framework.common.schema.schema_object.Number | list[superlinked.framework.common.schema.schema_object.Number], min_value: float | int, max_value: float | int, mode: superlinked.framework.common.embedding.number_embedding.Mode, negative_filter: float = 0.0)`
:   NumberSpace is used to encode numerical values within a specified range.
    The range is defined by the min_value and max_value parameters.
    The preference can be controlled by the mode parameter.
    
    Attributes:
        number (SpaceFieldSet): A set of Number objects.
            It is a SchemaFieldObject not regular python ints or floats.
        min_value (float | int): This represents the minimum boundary. Any number lower than
            this will be considered as this minimum value. It can be either a float or an integer.
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
        mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
            Similar mode expects a .similar on the query, otherwise it will default to maximum.
        negative_filter (float): This is a value that will be set for everything that is equal or
            lower than the min_value. It can be a float. It defaults to 0 (No effect)
    
    Raises:
        InvalidSpaceParamException: If multiple fields of the same schema are in the same space.
        InvalidSchemaException: If there's no node corresponding to a given schema.
    
    Initialize the NumberSpace.
    
    Args:
        number (Number | list[Number]): A Number object or a list of Number objects.
            It can be Float or Integer
        min_value (float | int): This represents the minimum boundary. Any number lower than
            this will be considered as this minimum value. It can be either a float or an integer.
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
        mode (Mode): The mode of the number embedding. Possible values are: maximum, minimum and similar.
            Similar mode expects a .similar on the query, otherwise it will default to maximum.
        negative_filter (float): This is a value that will be set for everything that is equal or
            lower than the min_value. It can be a float. It defaults to 0 (No effect)

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC