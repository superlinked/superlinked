Module superlinked.framework.dsl.query.query_clause.overriden_now_clause
========================================================================

Classes
-------

`OverriddenNowClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam])`
:   OverriddenNowClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]])

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Static methods

    `from_param(now: IntParamType) ‑> superlinked.framework.dsl.query.query_clause.overriden_now_clause.OverriddenNowClause`
    :

    ### Methods

    `get_altered_query_vector_params(self, query_vector_params: QueryVectorClauseParams, index_node_id: str, query_schema: IdSchemaObject, storage_manager: StorageManager) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :