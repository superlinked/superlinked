Module superlinked.framework.dsl.space.number_space
===================================================

Classes
-------

`NumberSpace(number: superlinked.framework.common.schema.schema_object.Number | list[superlinked.framework.common.schema.schema_object.Number], min_value: float | int, max_value: float | int, ordering: superlinked.framework.common.embedding.number_embedding.DistributionOrdering)`
:   NumberSpace is used to encode numerical values within a specified range.
    The range is defined by the min_value and max_value parameters.
    The ordering of the distribution can be controlled by the ordering parameter.
    
    Attributes:
        number (SpaceFieldSet): A set of Number objects.
            It is a SchemaFieldObject not regular python ints or floats.
        min_value (float | int): This represents the minimum boundary. Any number lower than
            this will be considered as this minimum value. It can be either a float or an integer.
        max_value (float | int): This represents the maximum boundary. Any number higher than
            this will be considered as this maximum value. It can be either a float or an integer.
        ordering (DistributionOrdering): The ordering of the distribution.
            Possible values are: ascending and descending.
    
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
        ordering (DistributionOrdering): The ordering of the distribution.
            Possible values are: ascending and descending.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC