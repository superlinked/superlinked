Module superlinked.framework.dsl.query.query_clause.radius_clause
=================================================================

Classes
-------

`RadiusClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam])`
:   RadiusClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]])

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Static methods

    `from_param(radius: NumericParamType | None) ‑> superlinked.framework.dsl.query.query_clause.radius_clause.RadiusClause`
    :

    ### Methods

    `get_altered_knn_search_params(self, partial_params: KNNSearchClauseParams) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :