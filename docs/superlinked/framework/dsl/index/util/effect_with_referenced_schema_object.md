Module superlinked.framework.dsl.index.util.effect_with_referenced_schema_object
================================================================================

Classes
-------

`EffectWithReferencedSchemaObject(base_effect: Effect, resolved_affected_schema_reference: ResolvedSchemaReference, resolved_affecting_schema_reference: ResolvedSchemaReference, event_schema: EventSchemaObject)`
:   EffectWithReferencedSchemaObject(base_effect: 'Effect', resolved_affected_schema_reference: 'ResolvedSchemaReference', resolved_affecting_schema_reference: 'ResolvedSchemaReference', event_schema: 'EventSchemaObject')

    ### Class variables

    `base_effect: superlinked.framework.dsl.index.effect.Effect`
    :

    `event_schema: superlinked.framework.common.schema.event_schema_object.EventSchemaObject`
    :

    `resolved_affected_schema_reference: superlinked.framework.common.dag.resolved_schema_reference.ResolvedSchemaReference`
    :

    `resolved_affecting_schema_reference: superlinked.framework.common.dag.resolved_schema_reference.ResolvedSchemaReference`
    :

    ### Static methods

    `from_base_effect(base_effect: Effect, schemas: set[SchemaObject]) ‑> superlinked.framework.dsl.index.util.effect_with_referenced_schema_object.EffectWithReferencedSchemaObject`
    :

    ### Instance variables

    `dag_effect: superlinked.framework.common.dag.dag_effect.DagEffect`
    :