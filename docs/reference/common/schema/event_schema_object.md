Module superlinked.framework.common.schema.event_schema_object
==============================================================

Classes
-------

`CreatedAtField(schema_obj: SchemaObjectT, created_at_field_name: str)`
:   A class representing creation time. A unix timestamp field in a schema object.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

    ### Methods

    `as_type(self, value: Any) ‑> int`
    :

`EventSchemaObject(base_cls: type, id_field_name: str, created_at_field_name: str)`
:   Custom decorated event schema class.
    Event schemas can be used to reference other schema and to define interactions between schemas.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.id_schema_object.IdSchemaObject
    * superlinked.framework.common.schema.schema_object.SchemaObject
    * abc.ABC

    ### Descendants

    * superlinked.framework.common.schema.event_schema.EventSchema

    ### Static methods

    `get_schema_field_type() ‑> types.UnionType`
    :

    ### Instance variables

    `created_at: CreatedAtField`
    :

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

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :