Module superlinked.framework.dsl.query.query_clause.nlq_system_prompt_clause
============================================================================

Classes
-------

`NLQSystemPromptClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam])`
:   NLQSystemPromptClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]])

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Static methods

    `from_param(system_prompt: StringParamType) ‑> superlinked.framework.dsl.query.query_clause.nlq_system_prompt_clause.NLQSystemPromptClause`
    :

    ### Methods

    `get_altered_nql_params(self, nlq_clause_params: NLQClauseParams) ‑> superlinked.framework.dsl.query.clause_params.NLQClauseParams`
    :