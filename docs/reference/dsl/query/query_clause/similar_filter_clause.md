Module superlinked.framework.dsl.query.query_clause.similar_filter_clause
=========================================================================

Classes
-------

`SimilarFilterClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], weight_param: TypedParam | Evaluated[TypedParam], field_set: SpaceFieldSet)`
:   SimilarFilterClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], weight_param: 'TypedParam | Evaluated[TypedParam]', field_set: 'SpaceFieldSet')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.NLQCompatible
    * abc.ABC

    ### Class variables

    `field_set: superlinked.framework.dsl.space.space_field_set.SpaceFieldSet`
    :

    `weight_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :

    ### Static methods

    `from_param(spaces: Sequence[Space], field_set: SpaceFieldSet, param: ParamType, weight: NumericParamType) ‑> superlinked.framework.dsl.query.query_clause.similar_filter_clause.SimilarFilterClause`
    :

    ### Instance variables

    `annotation_by_space_annotation: dict[str, str]`
    :

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    ### Methods

    `get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) ‑> set[collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | tuple[str | None, str | None] | None]`
    :

    `get_altered_query_vector_params(self, query_vector_params: QueryVectorClauseParams, index_node_id: str, query_schema: IdSchemaObject, storage_manager: StorageManager) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :

    `get_default_value_by_param_name(self) ‑> dict[str, typing.Any]`
    :

    `get_weight_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space | None, str]`
    :