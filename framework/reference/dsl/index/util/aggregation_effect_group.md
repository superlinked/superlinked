Module superlinked.framework.dsl.index.util.aggregation_effect_group
====================================================================

Classes
-------

`AggregationEffectGroup(space: Space[AggregationInputT, EmbeddingInputT], affected_schema: IdSchemaObject, effects: Sequence[EffectWithReferencedSchemaObject[AggregationInputT, EmbeddingInputT]])`
:   Group of effects with the same space and affected schema.

    ### Ancestors (in MRO)

    * typing.Generic

    ### Instance variables

    `affected_schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject`
    :

    `effects: Sequence[superlinked.framework.dsl.index.util.effect_with_referenced_schema_object.EffectWithReferencedSchemaObject[~AggregationInputT, ~EmbeddingInputT]]`
    :

    `space: superlinked.framework.dsl.space.space.Space[~AggregationInputT, ~EmbeddingInputT]`
    :