Module superlinked.framework.dsl.index.index
============================================

Classes
-------

`Index(spaces: superlinked.framework.dsl.space.space.Space | list[superlinked.framework.dsl.space.space.Space], effects: list[superlinked.framework.dsl.index.effect.Effect] | None = None)`
:   An index is an abstraction which represents a collection of spaces that will enable us to query our data.
    
    Initialize the Index.
    
    Args:
        spaces (Space | list[Space]): The space or list of spaces.
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