Module superlinked.framework.common.schema.schema_object
========================================================

Classes
-------

`SchemaField(name: str, schema_obj: SchemaObjectT, type_: type[SFT])`
:   A SchemaField is a generic field of your `@schema` decorated class.
    
    `SchemaField`s are the basic building block for inputs that will be referenced in an embedding space.
    Sub-types of a `SchemaField` are typed data representations that you can use to transform and load data
    to feed the vector embedding process.

    ### Ancestors (in MRO)

    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.common.schema.id_schema_object.IdField
    * superlinked.framework.common.schema.schema_object.String
    * superlinked.framework.common.schema.schema_object.Timestamp

`SchemaObject(base_cls: type, schema_name: str)`
:   `@schema` decorated class that has multiple `SchemaField`s.
    
    Use it to represent your structured data to reference during the vector embedding process.

    ### Descendants

    * superlinked.framework.common.schema.id_schema_object.IdSchemaObject

`String(name: str, schema_obj: SchemaObjectT)`
:   Field of a schema that stores a string value.
    
    e.g.: `TextEmbeddingSpace` expects a String field as an input.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.common.schema.schema_reference.SchemaReference

`Timestamp(name: str, schema_obj: SchemaObjectT)`
:   Field of a schema that stores a unix timestamp.
    
    e.g.: `RecencySpace` expects a Timestamp field as an input.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic