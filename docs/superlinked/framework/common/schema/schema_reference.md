Module superlinked.framework.common.schema.schema_reference
===========================================================

Classes
-------

`MultipliedSchemaReference(schema_reference: SchemaReference, multiplier: float = 1.0)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * superlinked.framework.common.interface.has_multiplier.HasMultiplier
    * abc.ABC

`SchemaReference(name: str, schema_obj: SchemaObject, referenced_schema: type[RST])`
:   Schema reference used within an `EventSchema` to reference other schemas.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.String
    * superlinked.framework.common.schema.schema_object.SchemaField
    * typing.Generic
    * superlinked.framework.common.interface.has_multiplier.HasMultiplier
    * abc.ABC