Module superlinked.framework.dsl.index.index_validator
======================================================

Classes
-------

`IndexValidator()`
:   

    ### Static methods

    `validate_effects(effects: superlinked.framework.dsl.index.effect.Effect | collections.abc.Sequence[superlinked.framework.dsl.index.effect.Effect] | None, spaces: Sequence[superlinked.framework.dsl.space.space.Space]) ‑> list[superlinked.framework.dsl.index.effect.Effect]`
    :

    `validate_fields(fields: superlinked.framework.common.schema.schema_object.SchemaField | collections.abc.Sequence[superlinked.framework.common.schema.schema_object.SchemaField | None] | None) ‑> Sequence[superlinked.framework.common.schema.schema_object.SchemaField]`
    :

    `validate_fields_to_exclude(fields_to_exclude: superlinked.framework.common.schema.schema_object.SchemaField | collections.abc.Sequence[superlinked.framework.common.schema.schema_object.SchemaField | None] | None) ‑> Sequence[superlinked.framework.common.schema.schema_object.SchemaField]`
    :

    `validate_spaces(spaces: superlinked.framework.dsl.space.space.Space | collections.abc.Sequence[superlinked.framework.dsl.space.space.Space]) ‑> list[superlinked.framework.dsl.space.space.Space]`
    :