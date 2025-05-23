Module superlinked.framework.common.schema.schema_object
========================================================

Classes
-------

`Blob(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a local/remote file path or an utf-8 encoded bytes string.
    
    e.g.: `ImageSpace` expects a blob field as an input.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

    ### Methods

    `as_type(self, value: Any) ‑> superlinked.framework.common.schema.blob_information.BlobInformation`
    :

`Boolean(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a boolean.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

`DescribedBlob(blob: Blob, description: String)`
:   DescribedBlob(blob: 'Blob', description: 'String')

    ### Instance variables

    `blob: superlinked.framework.common.schema.schema_object.Blob`
    :

    `description: superlinked.framework.common.schema.schema_object.String`
    :

`Float(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a float.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.Number
    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

`FloatList(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a vector.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

    ### Methods

    `as_type(self, value: Any) ‑> list[float]`
    :

    `parse(self, value: list[float]) ‑> list[float]`
    :

`Integer(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents an integer.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.Number
    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

`Number(name: str, schema_obj: SchemaObjectT, type_: type[SFT], nullable: bool)`
:   Field of a schema that represents a union of Float and Integer.
    
    e.g.: `NumberSpace` expects a Number field as an input.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.common.schema.schema_object.Float
    * superlinked.framework.common.schema.schema_object.Integer

`SchemaField(name: str, schema_obj: SchemaObjectT, type_: type[SFT], nullable: bool)`
:   A SchemaField is a generic field of your `@schema` decorated class.
    
    `SchemaField`s are the basic building block for inputs that will be referenced in an embedding space.
    Sub-types of a `SchemaField` are typed data representations that you can use to transform and load data
    to feed the vector embedding process.

    ### Ancestors (in MRO)

    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.common.schema.event_schema_object.CreatedAtField
    * superlinked.framework.common.schema.event_schema_object.SchemaReference
    * superlinked.framework.common.schema.id_field.IdField
    * superlinked.framework.common.schema.schema_object.Blob
    * superlinked.framework.common.schema.schema_object.Boolean
    * superlinked.framework.common.schema.schema_object.FloatList
    * superlinked.framework.common.schema.schema_object.Number
    * superlinked.framework.common.schema.schema_object.String
    * superlinked.framework.common.schema.schema_object.StringList
    * superlinked.framework.common.schema.schema_object.Timestamp

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

    ### Methods

    `as_type(self, value: Any) ‑> ~SFT`
    :

    `parse(self, value: SFT) ‑> ~SFT`
    :

`SchemaObject(base_cls: type)`
:   `@schema` decorated class that has multiple `SchemaField`s.
    
    Use it to represent your structured data to reference during the vector embedding process.

    ### Descendants

    * superlinked.framework.common.schema.id_schema_object.IdSchemaObject

    ### Instance variables

    `schema_fields: Sequence[SchemaField]`
    :

`String(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a string value.
    
    e.g.: `TextEmbeddingSpace` expects a String field as an input.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

`StringList(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a list of strings.

    ### Ancestors (in MRO)

    * superlinked.framework.common.schema.schema_object.SchemaField
    * superlinked.framework.common.interface.comparison_operand.ComparisonOperand
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `supported_comparison_operation_types: Sequence[ComparisonOperationType]`
    :

    ### Methods

    `as_type(self, value: Any) ‑> list[str]`
    :

    `parse(self, value: list[str]) ‑> list[str]`
    :

`Timestamp(name: str, schema_obj: SchemaObjectT, nullable: bool)`
:   Field of a schema that represents a unix timestamp.
    
    e.g.: `RecencySpace` expects a Timestamp field as an input.

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