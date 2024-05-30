Module superlinked.framework.common.schema.event_schema_object
==============================================================

Classes
-------

`EventSchemaObject(base_cls: type, schema_name: str, id_field_name: str)`
:   Custom decorated event schema class.
    Event schemas can be used to reference other schema and to define interactions between schemas.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.id_schema_object.IdSchemaObject
    * superlinked.framework.common.schema.schema_object.SchemaObject

`MultipliedSchemaReference(schema_reference: SchemaReference[RST], multiplier: float = 1.0)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * superlinked.framework.common.interface.has_multiplier.HasMultiplier
    * abc.ABC
    * typing.Generic

`SchemaReference(name: str, schema_obj: EventSchemaObject, referenced_schema: type[RST])`
:   Schema reference used within an `EventSchema` to reference other schemas.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * superlinked.framework.common.interface.has_multiplier.HasMultiplier
    * abc.ABC
    * typing.Generic

    ### Static methods

    `join_values(values: Sequence[str]) ‑> str`
    :