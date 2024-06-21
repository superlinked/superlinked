Module superlinked.framework.dsl.index.util.event_aggregation_effect_group
==========================================================================

Classes
-------

`EventAggregationEffectGroup(key: GroupKey, effects: list[EffectWithReferencedSchemaObject])`
:   Group of effects with the same space, event schema, affected schema and affecting schema.

    ### Class variables

    `GroupKey`
    :

    `effects: list[superlinked.framework.dsl.index.util.effect_with_referenced_schema_object.EffectWithReferencedSchemaObject]`
    :

    `key: superlinked.framework.dsl.index.util.event_aggregation_effect_group.EventAggregationEffectGroup.GroupKey`
    :

    ### Static methods

    `group_by_event_and_affecting_schema(effects: list[EffectWithReferencedSchemaObject]) ‑> list[superlinked.framework.dsl.index.util.event_aggregation_effect_group.EventAggregationEffectGroup]`
    :