Module superlinked.framework.dsl.query.query_clause.nlq_clause
==============================================================

Classes
-------

`NLQClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], client_config: OpenAIClientConfig)`
:   NLQClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], client_config: 'OpenAIClientConfig')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Class variables

    `client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig`
    :

    ### Static methods

    `from_param(natural_query: StringParamType, client_config: OpenAIClientConfig) ‑> superlinked.framework.dsl.query.query_clause.nlq_clause.NLQClause`
    :

    ### Methods

    `get_altered_nql_params(self, nlq_clause_params: NLQClauseParams) ‑> superlinked.framework.dsl.query.clause_params.NLQClauseParams`
    :