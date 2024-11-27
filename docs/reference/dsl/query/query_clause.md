Module superlinked.framework.dsl.query.query_clause
===================================================

Classes
-------

`HardFilterClause(value_param: Param | Evaluated[Param], op: ComparisonOperationType, operand: SchemaField, group_key: int | None)`
:   HardFilterClause(value_param: 'Param | Evaluated[Param]', op: 'ComparisonOperationType', operand: 'SchemaField', group_key: 'int | None')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Class variables

    `group_key: int | None`
    :

    `op: superlinked.framework.common.interface.comparison_operation_type.ComparisonOperationType`
    :

    `operand: superlinked.framework.common.schema.schema_object.SchemaField`
    :

    ### Methods

    `evaluate(self) ‑> superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField] | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`LimitClause(value_param: Param | Evaluated[Param])`
:   LimitClause(value_param: 'Param | Evaluated[Param]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Methods

    `evaluate(self) ‑> int`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> int`
    :

`LooksLikeFilterClause(value_param: Param | Evaluated[Param], weight_param: Param | Evaluated[Param], schema_field: SchemaField)`
:   LooksLikeFilterClause(value_param: 'Param | Evaluated[Param]', weight_param: 'Param | Evaluated[Param]', schema_field: 'SchemaField')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.WeightedQueryClause
    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Class variables

    `schema_field: superlinked.framework.common.schema.schema_object.SchemaField`
    :

    ### Methods

    `evaluate(self) ‑> superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.LooksLikePredicate] | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_default_weight_param_name(self) ‑> str`
    :

`NLQClause(value_param: Param | Evaluated[Param], client_config: OpenAIClientConfig)`
:   NLQClause(value_param: 'Param | Evaluated[Param]', client_config: 'OpenAIClientConfig')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Class variables

    `client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig`
    :

    ### Methods

    `evaluate(self) ‑> str | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`NLQSystemPromptClause(value_param: Param | Evaluated[Param])`
:   NLQSystemPromptClause(value_param: 'Param | Evaluated[Param]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Methods

    `evaluate(self) ‑> str | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`OverriddenNowClause(value_param: Param | Evaluated[Param])`
:   OverriddenNowClause(value_param: 'Param | Evaluated[Param]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Methods

    `evaluate(self) ‑> int | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`QueryClause(value_param: Param | Evaluated[Param])`
:   QueryClause(value_param: 'Param | Evaluated[Param]')

    ### Ancestors (in MRO)

    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.query.query_clause.HardFilterClause
    * superlinked.framework.dsl.query.query_clause.LimitClause
    * superlinked.framework.dsl.query.query_clause.NLQClause
    * superlinked.framework.dsl.query.query_clause.NLQSystemPromptClause
    * superlinked.framework.dsl.query.query_clause.OverriddenNowClause
    * superlinked.framework.dsl.query.query_clause.RadiusClause
    * superlinked.framework.dsl.query.query_clause.SpaceWeightClause
    * superlinked.framework.dsl.query.query_clause.WeightedQueryClause

    ### Class variables

    `value_param: superlinked.framework.dsl.query.param.Param | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.param.Param]`
    :

    ### Methods

    `alter_value(self, params: dict[str, Any], is_override_set: bool) ‑> Self`
    :

    `evaluate(self) ‑> ~EvaluatedQueryT`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_param(self, param: Param | Evaluated[Param]) ‑> superlinked.framework.dsl.query.param.Param`
    :

    `get_param_value(self, param: Param | Evaluated[Param]) ‑> collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | None | tuple[str | None, str | None]`
    :

    `get_value(self) ‑> float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation | None`
    :

`RadiusClause(value_param: Param | Evaluated[Param])`
:   RadiusClause(value_param: 'Param | Evaluated[Param]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Methods

    `evaluate(self) ‑> float | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> float | None`
    :

`SimilarFilterClause(value_param: Param | Evaluated[Param], weight_param: Param | Evaluated[Param], field_set: SpaceFieldSet, schema_field: SchemaField)`
:   SimilarFilterClause(value_param: 'Param | Evaluated[Param]', weight_param: 'Param | Evaluated[Param]', field_set: 'SpaceFieldSet', schema_field: 'SchemaField')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.WeightedQueryClause
    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Class variables

    `field_set: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `schema_field: superlinked.framework.common.schema.schema_object.SchemaField`
    :

    ### Instance variables

    `space: Space`
    :

    ### Methods

    `evaluate(self) ‑> tuple[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.SimilarPredicate]] | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_default_weight_param_name(self) ‑> str`
    :

`SpaceWeightClause(value_param: Param | Evaluated[Param], space: Space)`
:   SpaceWeightClause(value_param: 'Param | Evaluated[Param]', space: 'Space')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Class variables

    `space: superlinked.framework.dsl.space.space.Space`
    :

    ### Methods

    `evaluate(self) ‑> tuple[superlinked.framework.dsl.space.space.Space, float]`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> float`
    :

`WeightedQueryClause(value_param: Param | Evaluated[Param], weight_param: Param | Evaluated[Param])`
:   WeightedQueryClause(value_param: 'Param | Evaluated[Param]', weight_param: 'Param | Evaluated[Param]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.query.query_clause.LooksLikeFilterClause
    * superlinked.framework.dsl.query.query_clause.SimilarFilterClause

    ### Class variables

    `weight_param: superlinked.framework.dsl.query.param.Param | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.param.Param]`
    :

    ### Methods

    `alter_weight(self, params: dict[str, Any], is_override_set: bool) ‑> Self`
    :

    `get_default_weight_param_name(self) ‑> str`
    :

    `get_weight(self) ‑> float`
    :