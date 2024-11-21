Module superlinked.framework.dsl.index.index
============================================

Classes
-------

`Index(spaces: Union[superlinked.framework.dsl.space.space.Space, Annotated[list[superlinked.framework.dsl.space.space.Space], beartype.vale.Is[TypeValidator.list_validator.validator]]], fields: Union[superlinked.framework.common.schema.schema_object.SchemaField, Annotated[list[superlinked.framework.common.schema.schema_object.SchemaField], beartype.vale.Is[TypeValidator.list_validator.validator]], ForwardRef(None)] = None, effects: Union[superlinked.framework.dsl.index.effect.Effect, Annotated[list[superlinked.framework.dsl.index.effect.Effect], beartype.vale.Is[TypeValidator.list_validator.validator]], ForwardRef(None)] = None, max_age: datetime.timedelta | None = None, max_count: int | None = None, temperature: int | float = 0.5, event_influence: int | float = 0.5, time_decay_floor: int | float = 1.0)`
:   An index is an abstraction which represents a collection of spaces that will enable us to query our data.
    
    Initialize the Index.
    
    Args:
        spaces (Space | list[Space]): The space or list of spaces.
        fields (SchemaField | list[SchemaField]): The field or list of fields to be indexed.
        effects (Effect | list[Effect]): A list of conditional interactions within a `Space`.
            Defaults to None.
        max_age (datetime.timedelta | None): Maximum age of events to be considered. Older events
            will be filtered out, if specified. Defaults to None meaning no restriction.
        max_count (int | None): Only affects the batch system! Restricts how many events should be considered,
            based on their age. Defaults to None meaning no restriction.
        temperature (float): Controls how much each event contributes when aggregating events together.
            Must be between 0 and 1. Values closer to 0 give more weight to the stored event aggregate,
            while values closer to 1 give more weight to the new event being added. Defaults to 0.5 for
            balanced weighting.
        event_influence (float): Controls how much the final aggregated event vector influences the base vector.
            Must be between 0 and 1. Values closer to 0 keep the result closer to the base vector, while values
            closer to 1 make the result more influenced by the aggregated events.
            Defaults to 0.5 for balanced influence.
        time_decay_floor (float): Controls the time decay curve for event weights.
            Higher values create a more gradual decay, while lower values create steeper decay.
            Defaults to 1.0.
    
    Raises:
        InitializationException: If no spaces are provided.

    ### Methods

    `has_schema(self, schema: superlinked.framework.common.schema.schema_object.SchemaObject) ‑> bool`
    :   Check, if the given schema is listed as an input to any of the spaces of the index.
        
        Args:
            schema (SchemaObject): The schema to check.
        
        Returns:
            bool: True if the index has the schema, False otherwise.

    `has_space(self, space: superlinked.framework.dsl.space.space.Space) ‑> bool`
    :   Check, if the given space is present in the index.
        
        Args:
            space (Space): The space to check.
        
        Returns:
            bool: True if the index has the space, False otherwise.