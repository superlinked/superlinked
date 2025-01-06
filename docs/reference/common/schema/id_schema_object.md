Module superlinked.framework.common.schema.id_schema_object
===========================================================

Classes
-------

`IdField(schema_obj: ~SchemaObjectT, id_field_name: str)`
:   A class representing an ID field in a schema object.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

`IdSchemaObject(base_cls: type, id_field_name: str)`
:   Schema object with required ID field.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaObject
    * abc.ABC

    ### Descendants

    * superlinked.framework.common.schema.event_schema_object.EventSchemaObject
    * superlinked.framework.common.schema.schema.Schema

    ### Static methods

    `get_schema_field_type() ‑> types.UnionType`
    :

    ### Instance variables

    `id: superlinked.framework.common.schema.id_schema_object.IdField`
    :