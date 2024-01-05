Module superlinked.framework.dsl.index.util.event_aggregation_effect_group
==========================================================================

Classes
-------

`EventAggregationEffectGroup(space: Space, event_schema: EventSchemaObject, complete_affected_schema_reference: CompleteSchemaReference, complete_affecting_schema_reference: CompleteSchemaReference, effects: list[EffectWithReferencedSchemaObject])`
:   Group of effects with the same space, event schema, affected schema and affecting schema.

    ### Class variables

    `complete_affected_schema_reference: superlinked.framework.dsl.index.util.complete_schema_reference.CompleteSchemaReference`
    :

    `complete_affecting_schema_reference: superlinked.framework.dsl.index.util.complete_schema_reference.CompleteSchemaReference`
    :

    `effects: list[superlinked.framework.dsl.index.util.effect_with_referenced_schema_object.EffectWithReferencedSchemaObject]`
    :

    `event_schema: superlinked.framework.common.schema.event_schema_object.EventSchemaObject`
    :

    `space: superlinked.framework.dsl.space.space.Space`
    :

    ### Static methods

    `from_filtered_effects(filtered_effects: list[EffectWithReferencedSchemaObject]) ‑> superlinked.framework.dsl.index.util.event_aggregation_effect_group.EventAggregationEffectGroup`
    :