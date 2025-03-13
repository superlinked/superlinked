Module superlinked.framework.dsl.query.nlq.nlq_handler
======================================================

Classes
-------

`NLQHandler(client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig)`
:   

    ### Methods

    `fill_params(self, natural_query: str, clauses: Sequence[superlinked.framework.dsl.query.query_clause.query_clause.QueryClause], space_weight_param_info: superlinked.framework.dsl.query.space_weight_param_info.SpaceWeightParamInfo, system_prompt: str | None = None) ‑> dict[str, typing.Any]`
    :

    `suggest_improvements(self, clauses: Sequence[superlinked.framework.dsl.query.query_clause.query_clause.QueryClause], space_weight_param_info: superlinked.framework.dsl.query.space_weight_param_info.SpaceWeightParamInfo, natural_query: str | None, feedback: str | None, system_prompt: str | None = None) ‑> superlinked.framework.dsl.query.nlq.suggestion.query_suggestion_model.QuerySuggestionsModel`
    :