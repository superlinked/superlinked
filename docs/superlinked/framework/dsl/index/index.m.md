Module superlinked.framework.dsl.index.index
============================================

Classes
-------

`Index(spaces: Union[superlinked.framework.dsl.space.space.Space, Annotated[list[superlinked.framework.dsl.space.space.Space], Is[TypeValidator.list_validator.validator]]], fields: Union[superlinked.framework.common.schema.schema_object.SchemaField, Annotated[list[superlinked.framework.common.schema.schema_object.SchemaField], Is[TypeValidator.list_validator.validator]], ForwardRef(None)] = None, effects: Optional[typing.Annotated[list[superlinked.framework.dsl.index.effect.Effect], Is[TypeValidator.list_validator.validator]]] = None)`
:   An index is an abstraction which represents a collection of spaces that will enable us to query our data.
    
    Initialize the Index.
    
    Args:
        spaces (Space | list[Space]): The space or list of spaces.
        fields (SchemaField | list[SchemaField]): The field or list of fields to be indexed.
        effects (list[Effect]): A list of conditional interactions within a `Space`.
        Defaults to None.
    
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