Module superlinked.framework.dsl.index.effect
=============================================

Classes
-------

`Effect(space: superlinked.framework.dsl.space.space.Space, affected_schema_reference: superlinked.framework.common.schema.schema_reference.SchemaReference[~ADST], affecting_schema_reference: superlinked.framework.common.schema.schema_reference.SchemaReference[~AGST], filter_: superlinked.framework.common.schema.schema_object.SchemaFieldBinaryOp)`
:   An effect represents a conditional interaction within a `Space` where the
    `affecting_schema_reference` intercated with the `affected_schema_reference`.
    
    It allows you to real-time adjust embeddings based on interaction.
    e.g.: A `User` schema interacts with a `Post` schema, if `event.type == 'like'.

    ### Ancestors (in MRO)

    * typing.Generic

    ### Class variables

    `affected_schema_reference: superlinked.framework.common.schema.schema_reference.SchemaReference[~ADST]`
    :

    `affecting_schema_reference: superlinked.framework.common.schema.schema_reference.SchemaReference[~AGST]`
    :

    `filter_: superlinked.framework.common.schema.schema_object.SchemaFieldBinaryOp`
    :

    `space: superlinked.framework.dsl.space.space.Space`
    :