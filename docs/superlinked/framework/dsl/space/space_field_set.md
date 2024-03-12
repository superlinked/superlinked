Module superlinked.framework.dsl.space.space_field_set
======================================================

Classes
-------

`SpaceFieldSet(space: superlinked.framework.dsl.space.space.Space, fields: set[superlinked.framework.common.schema.schema_object.SchemaField])`
:   A class representing a set of fields in a space.
    Attributes:
        space (Space): The space.
        fields (set[SchemaField]): The set of fields.

    ### Class variables

    `fields: set[superlinked.framework.common.schema.schema_object.SchemaField]`
    :

    `space: superlinked.framework.dsl.space.space.Space`
    :

    ### Methods

    `get_field_for_schema(self, schema_: Any) ‑> superlinked.framework.common.schema.schema_object.SchemaField | None`
    :