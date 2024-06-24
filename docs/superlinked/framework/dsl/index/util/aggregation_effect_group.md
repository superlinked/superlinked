Module superlinked.framework.dsl.index.util.aggregation_effect_group
====================================================================

Classes
-------

`AggregationEffectGroup(space: Space, affected_schema: SchemaObject, effects: list[EffectWithReferencedSchemaObject])`
:   Group of effects with the same space and affected schema.

    ### Class variables

    `affected_schema: superlinked.framework.common.schema.schema_object.SchemaObject`
    :

    `effects: list[superlinked.framework.dsl.index.util.effect_with_referenced_schema_object.EffectWithReferencedSchemaObject]`
    :

    `space: superlinked.framework.dsl.space.space.Space`
    :

    ### Static methods

    `from_filtered_effects(filtered_effects: list[EffectWithReferencedSchemaObject]) ‑> superlinked.framework.dsl.index.util.aggregation_effect_group.AggregationEffectGroup`
    :