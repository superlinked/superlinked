Module superlinked.framework.common.schema.id_schema_object
===========================================================

Classes
-------

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

    `id: superlinked.framework.common.schema.id_field.IdField`
    :