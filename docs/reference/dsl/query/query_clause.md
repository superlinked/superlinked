Module superlinked.framework.dsl.query.query_clause
===================================================

Classes
-------

`HardFilterClause(value_param: TypedParam | Evaluated[TypedParam], op: ComparisonOperationType, operand: SchemaField, group_key: int | None)`
:   HardFilterClause(value_param: 'TypedParam | Evaluated[TypedParam]', op: 'ComparisonOperationType', operand: 'SchemaField', group_key: 'int | None')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic
    * superlinked.framework.common.interface.has_annotation.HasAnnotation
    * abc.ABC

    ### Class variables

    `group_key: int | None`
    :

    `op: superlinked.framework.common.interface.comparison_operation_type.ComparisonOperationType`
    :

    `operand: superlinked.framework.common.schema.schema_object.SchemaField`
    :

    ### Static methods

    `from_param(operation: ComparisonOperation[SchemaField]) ‑> superlinked.framework.dsl.query.query_clause.HardFilterClause`
    :

    ### Instance variables

    `annotation: str`
    :

    `is_type_mandatory_in_nlq: bool`
    :

    ### Methods

    `evaluate(self) ‑> superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField] | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`LimitClause(value_param: TypedParam | Evaluated[TypedParam])`
:   LimitClause(value_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Static methods

    `from_param(limit: IntParamType) ‑> superlinked.framework.dsl.query.query_clause.LimitClause`
    :

    ### Methods

    `evaluate(self) ‑> int`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> int`
    :

`LooksLikeFilterClause(value_param: TypedParam | Evaluated[TypedParam], schema_field: SchemaField, weight_param: TypedParam | Evaluated[TypedParam] | dict[Space, TypedParam | Evaluated[TypedParam]])`
:   LooksLikeFilterClause(value_param: 'TypedParam | Evaluated[TypedParam]', schema_field: 'SchemaField', weight_param: 'TypedParam | Evaluated[TypedParam] | dict[Space, TypedParam | Evaluated[TypedParam]]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic
    * superlinked.framework.common.interface.has_annotation.HasAnnotation
    * abc.ABC

    ### Class variables

    `schema_field: superlinked.framework.common.schema.schema_object.SchemaField`
    :

    `weight_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam] | dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]]`
    :

    ### Static methods

    `from_param(id_: IdField, id_param: StringParamType, weight: NumericParamType | Mapping[Space, NumericParamType]) ‑> superlinked.framework.dsl.query.query_clause.LooksLikeFilterClause`
    :

    ### Instance variables

    `annotation: str`
    :

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    `weight_param_names: list[str]`
    :

    ### Methods

    `evaluate(self) ‑> tuple[str, float | dict[str, float]] | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_default_weight_param_name(self) ‑> str`
    :

    `get_param_value_by_param_name(self) ‑> dict[str, float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation | None]`
    :

    `set_defaults_for_nlq(self) ‑> Self`
    :

`NLQClause(value_param: TypedParam | Evaluated[TypedParam], client_config: OpenAIClientConfig)`
:   NLQClause(value_param: 'TypedParam | Evaluated[TypedParam]', client_config: 'OpenAIClientConfig')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Class variables

    `client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig`
    :

    ### Static methods

    `from_param(natural_query: StringParamType, client_config: OpenAIClientConfig) ‑> superlinked.framework.dsl.query.query_clause.NLQClause`
    :

    ### Methods

    `evaluate(self) ‑> str | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`NLQSystemPromptClause(value_param: TypedParam | Evaluated[TypedParam])`
:   NLQSystemPromptClause(value_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Static methods

    `from_param(system_prompt: StringParamType) ‑> superlinked.framework.dsl.query.query_clause.NLQSystemPromptClause`
    :

    ### Methods

    `evaluate(self) ‑> str | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`OverriddenNowClause(value_param: TypedParam | Evaluated[TypedParam])`
:   OverriddenNowClause(value_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Static methods

    `from_param(now: IntParamType) ‑> superlinked.framework.dsl.query.query_clause.OverriddenNowClause`
    :

    ### Methods

    `evaluate(self) ‑> int | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

`QueryClause(value_param: TypedParam | Evaluated[TypedParam])`
:   QueryClause(value_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * typing.Generic

    ### Descendants

    * superlinked.framework.dsl.query.query_clause.HardFilterClause
    * superlinked.framework.dsl.query.query_clause.LimitClause
    * superlinked.framework.dsl.query.query_clause.LooksLikeFilterClause
    * superlinked.framework.dsl.query.query_clause.NLQClause
    * superlinked.framework.dsl.query.query_clause.NLQSystemPromptClause
    * superlinked.framework.dsl.query.query_clause.OverriddenNowClause
    * superlinked.framework.dsl.query.query_clause.RadiusClause
    * superlinked.framework.dsl.query.query_clause.SelectClause
    * superlinked.framework.dsl.query.query_clause.SimilarFilterClause
    * superlinked.framework.dsl.query.query_clause.SpaceWeightClause

    ### Class variables

    `value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :

    ### Static methods

    `get_param(typed_param: TypedParam | Evaluated[TypedParam]) ‑> superlinked.framework.dsl.query.param.Param`
    :

    `get_param_value(param: TypedParam | Evaluated[TypedParam]) ‑> collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | None | tuple[str | None, str | None]`
    :

    `get_typed_param(typed_param: TypedParam | Evaluated[TypedParam]) ‑> superlinked.framework.dsl.query.typed_param.TypedParam`
    :

    `get_value_by_param_name(param: TypedParam | Evaluated[TypedParam]) ‑> dict[str, collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | None | tuple[str | None, str | None]]`
    :

    ### Instance variables

    `is_type_mandatory_in_nlq: bool`
    :

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    `value_param_name: str`
    :

    ### Methods

    `alter_param_values(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) ‑> Self`
    :

    `evaluate(self) ‑> ~EvaluatedQueryT`
    :

    `get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) ‑> set[collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | None | tuple[str | None, str | None]]`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space, str]`
    :

    `get_param_value_by_param_name(self) ‑> dict[str, float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation | None]`
    :

    `get_value(self) ‑> float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation | None`
    :

    `set_defaults_for_nlq(self) ‑> Self`
    :

`RadiusClause(value_param: TypedParam | Evaluated[TypedParam])`
:   RadiusClause(value_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Static methods

    `from_param(radius: NumericParamType | None) ‑> superlinked.framework.dsl.query.query_clause.RadiusClause`
    :

    ### Methods

    `evaluate(self) ‑> float | None`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> float | None`
    :

`SelectClause(value_param: TypedParam | Evaluated[TypedParam])`
:   SelectClause(value_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic

    ### Static methods

    `from_param(param: Param | Sequence[str]) ‑> superlinked.framework.dsl.query.query_clause.SelectClause`
    :

    ### Methods

    `evaluate(self) ‑> list[str]`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> list[str]`
    :

`SimilarFilterClause(value_param: TypedParam | Evaluated[TypedParam], weight_param: TypedParam | Evaluated[TypedParam], field_set: SpaceFieldSet)`
:   SimilarFilterClause(value_param: 'TypedParam | Evaluated[TypedParam]', weight_param: 'TypedParam | Evaluated[TypedParam]', field_set: 'SpaceFieldSet')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic
    * superlinked.framework.common.interface.has_annotation.HasAnnotation
    * abc.ABC

    ### Class variables

    `field_set: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `weight_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :

    ### Static methods

    `from_param(field_set: SpaceFieldSet, param: ParamType, weight: NumericParamType) ‑> superlinked.framework.dsl.query.query_clause.SimilarFilterClause`
    :

    ### Instance variables

    `annotation: str`
    :

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    `space: Space`
    :

    ### Methods

    `evaluate(self) ‑> tuple[superlinked.framework.dsl.space.space.Space, superlinked.framework.common.interface.weighted.Weighted[float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation]] | None`
    :

    `get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) ‑> set[collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | None | tuple[str | None, str | None]]`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space, str]`
    :

    `get_param_value_by_param_name(self) ‑> dict[str, float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation | None]`
    :

`SpaceWeightClause(value_param: TypedParam | Evaluated[TypedParam], space: Space)`
:   SpaceWeightClause(value_param: 'TypedParam | Evaluated[TypedParam]', space: 'Space')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.QueryClause
    * typing.Generic
    * superlinked.framework.common.interface.has_annotation.HasAnnotation
    * abc.ABC

    ### Class variables

    `space: superlinked.framework.dsl.space.space.Space`
    :

    ### Static methods

    `from_param(weight: NumericParamType, space: Space) ‑> superlinked.framework.dsl.query.query_clause.SpaceWeightClause`
    :

    ### Instance variables

    `annotation: str`
    :

    ### Methods

    `evaluate(self) ‑> tuple[superlinked.framework.dsl.space.space.Space, float]`
    :

    `get_default_value_param_name(self) ‑> str`
    :

    `get_value(self) ‑> float`
    :