Module superlinked.framework.dsl.query.query_clause.looks_like_filter_clause
============================================================================

Classes
-------

`LooksLikeFilterClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], schema_field: IdField, weight_param: TypedParam | Evaluated[TypedParam])`
:   LooksLikeFilterClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], schema_field: 'IdField', weight_param: 'TypedParam | Evaluated[TypedParam]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.base_looks_like_filter_clause.BaseLooksLikeFilterClause
    * superlinked.framework.dsl.query.query_clause.query_clause.NLQCompatible
    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Static methods

    `from_param(id_: IdField, id_param: StringParamType, weight: NumericParamType) ‑> superlinked.framework.dsl.query.query_clause.looks_like_filter_clause.LooksLikeFilterClause`
    :

    ### Instance variables

    `nlq_annotations: list[NLQAnnotation]`
    :

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    `weight_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :

    ### Methods

    `get_default_value_by_param_name(self) ‑> dict[str, typing.Any]`
    :

    `get_weight_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space | None, str]`
    :